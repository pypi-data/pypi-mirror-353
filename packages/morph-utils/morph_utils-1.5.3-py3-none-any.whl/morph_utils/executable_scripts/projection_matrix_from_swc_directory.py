import os
from tqdm import tqdm
import pandas as pd
import argschema as ags
import time 
import subprocess
from morph_utils.ccf import projection_matrix_for_swc


class IO_Schema(ags.ArgSchema):
    ccf_swc_directory = ags.fields.InputDir(description='directory with micron resolution ccf registered files')
    output_directory = ags.fields.OutputDir(description="output directory")
    projection_threshold = ags.fields.Int(default=0)
    normalize_proj_mat = ags.fields.Boolean(default=True)
    mask_method = ags.fields.Str(default="tip_and_branch",description = " 'tip_and_branch', 'branch', 'tip', or 'tip_or_branch' ")
    count_method = ags.fields.String(default="node", description="should be a member of ['node','tip','branch']")
    annotation_path = ags.fields.Str(default="",description = "Optional. Path to annotation .nrrd file. Defaults to 10um ccf atlas")
    resolution = ags.fields.Int(default=10, description="Optional. ccf resolution (micron/pixel")
    volume_shape = ags.fields.List(ags.fields.Int, default=[1320, 800, 1140], description = "Optional. Size of input annotation")
    resample_spacing = ags.fields.Float(allow_none=True, default=None, description = 'internode spacing to resample input morphology with')
    run_host = ags.fields.String(default='local',description='either ["local" or "hpc"]. Will run either locally or submit jobs to the HPC')
    virtual_env_name = ags.fields.Str(default='skeleton_keys_4',description='Name of virtual conda env to activate on hpc. not needed if running local')
    output_projection_csv = ags.fields.OutputFile(description="output projection csv, when running local only")

    
def normalize_projection_columns_per_cell(input_df, projection_column_identifiers=['ipsi', 'contra']):
    """
    :param input_df:  input projection df
    :param projection_column_identifiers: list of identifiers for projection columns. i.e. strings that identify projection columns from metadata columns
    :return: normalized projection matrix
    """
    proj_cols = [c for c in input_df.columns if any([ider in c for ider in projection_column_identifiers])]
    input_df[proj_cols] = input_df[proj_cols].fillna(0)

    res = input_df[proj_cols].T / input_df[proj_cols].sum(axis=1)
    input_df[proj_cols] = res.T

    return input_df


def main(ccf_swc_directory, 
         output_directory, 
         resolution, 
         projection_threshold, 
         normalize_proj_mat,
         mask_method,
         count_method,
         annotation_path,
         volume_shape,
         resample_spacing,
         run_host,
         virtual_env_name,
         output_projection_csv,
         **kwargs):
    
    if run_host not in ['local','hpc']:
        raise ValueError(f"Invalid run_host parameter entered ({run_host})")
    if mask_method not in [None,'tip_and_branch', 'branch', 'tip', 'tip_or_branch']:
        raise ValueError(f"Invalid mask_method provided {mask_method}")
    
    if annotation_path == "":
        annotation_path = None
    
    if run_host == 'hpc':
            
        output_directory = os.path.abspath(output_directory)
        single_sp_proj_dir = os.path.join(output_directory,"SingleCellProjections")
        job_dir = os.path.join(output_directory,"JobDir")
        for dd in [single_sp_proj_dir, job_dir]:
            if not os.path.exists(dd):
                os.mkdir(dd)
                
    results = []
    single_cell_job_ids = []
    for swc_fn in tqdm([f for f in os.listdir(ccf_swc_directory) if ".swc" in f]):

        swc_pth = os.path.abspath(os.path.join(ccf_swc_directory, swc_fn))
        
        if run_host=='local':
            res = projection_matrix_for_swc(input_swc_file=swc_pth, 
                                count_method= count_method,
                                mask_method = mask_method,
                                annotation=None, 
                                annotation_path = annotation_path, 
                                volume_shape=volume_shape,
                                resolution=resolution,
                                resample_spacing= resample_spacing)
            results.append(res)

        else:
                
            this_output_projection_csv = os.path.join(single_sp_proj_dir, swc_fn.replace(".swc",".csv"))
            
            if not os.path.exists(this_output_projection_csv):
                    
                job_file = os.path.join(job_dir,swc_fn.replace(".swc",".sh"))
                log_file = os.path.join(job_dir,swc_fn.replace(".swc",".log"))
                
                command = "morph_utils_extract_projection_matrix_single_cell "
                command = command+ f" --input_swc_file '{swc_pth}'"
                command = command+ f" --output_projection_csv {this_output_projection_csv}"
                command = command+ f" --projection_threshold {projection_threshold}"
                command = command+ f" --normalize_proj_mat {normalize_proj_mat}"
                command = command+ f" --mask_method {mask_method}"
                command = command+ f" --count_method {count_method}"
                command = command+ f" --annotation_path {annotation_path}"
                command = command+ f" --resolution {resolution}"
                # command = command+ f" --volume_shape {volume_shape}"
                if resample_spacing is not None:
                    command = command+ f" --resample_spacing {resample_spacing}"

                    
                activate_command = f"source activate {virtual_env_name}"
                command_list = [activate_command, command]
                        
                slurm_kwargs = {
                    "--job-name": f"{swc_fn}",
                    "--mail-type": "NONE",
                    "--cpus-per-task": "1",
                    "--nodes": "1",
                    "--kill-on-invalid-dep": "yes",
                    "--mem": "24gb",
                    "--time": "1:00:00",
                    "--partition": "celltypes",
                    "--output": log_file
                }

                dag_node = {
                    "job_file":job_file,
                    "slurm_kwargs":slurm_kwargs,
                    "slurm_commands":command_list
                }
                
                job_file = dag_node["job_file"]
                slurm_kwargs = dag_node["slurm_kwargs"]
                command_list = dag_node["slurm_commands"]

                job_string_list = [f"#SBATCH {k}={v}" for k, v in slurm_kwargs.items()]
                job_string_list = job_string_list + command_list
                job_string_list = ["#!/bin/bash"] + job_string_list

                if os.path.exists(job_file):
                    os.remove(job_file)

                with open(job_file, 'w') as job_f:
                    for val in job_string_list:
                        job_f.write(val)
                        job_f.write('\n')
                        
                        
                command = "sbatch {}".format(job_file)
                command_list = command.split(" ")
                result = subprocess.run(command_list, stdout=subprocess.PIPE)
                std_out = result.stdout.decode('utf-8')

                job_id = std_out.split("Submitted batch job ")[-1].replace("\n", "")
                single_cell_job_ids.append(job_id)
                # time.sleep(0.1)
                
    if run_host!='local':
        # aggregate single projection files into proj mat
        job_file = os.path.join(job_dir,"Projection_Aggregation.sh")
        log_file = os.path.join(job_dir,"Projection_Aggregation.log")
        agg_outdir = os.path.join(output_directory,'SingleCellProjections')
        command = "morph_utils_aggregate_single_cell_projs "
        command = command+ f" --output_projection_csv {output_projection_csv}"
        command = command+ f" --output_directory {agg_outdir}"
        command = command+ f" --projection_threshold {projection_threshold}"
        command = command+ f" --normalize_proj_mat {normalize_proj_mat}"
        command = command+ f" --mask_method {mask_method}"
            
        activate_command = f"source activate {virtual_env_name}"
        command_list = [activate_command, command]
                
        slurm_kwargs = {
            "--job-name": "AggregateProjs",
            "--mail-type": "NONE",
            "--cpus-per-task": "1",
            "--nodes": "1",
            "--kill-on-invalid-dep": "yes",
            "--mem": "4gb",
            "--time": "1:00:00",
            "--partition": "celltypes",
            "--output": log_file
        }

        dag_node = {
            "job_file":job_file,
            "slurm_kwargs":slurm_kwargs,
            "slurm_commands":command_list
        }
        
        job_file = dag_node["job_file"]
        slurm_kwargs = dag_node["slurm_kwargs"]
        command_list = dag_node["slurm_commands"]

        job_string_list = [f"#SBATCH {k}={v}" for k, v in slurm_kwargs.items()]
        job_string_list = job_string_list + command_list
        job_string_list = ["#!/bin/bash"] + job_string_list

        if os.path.exists(job_file):
            os.remove(job_file)

        with open(job_file, 'w') as job_f:
            for val in job_string_list:
                job_f.write(val)
                job_f.write('\n')
                
        command = "sbatch --dependency=afterany"
        for p_jid in single_cell_job_ids:
            command = command + f":{p_jid}"
        command = command + " {}".format(job_file)
        command_list = command.split(" ")
        # print(command)
        result = subprocess.run(command_list, stdout=subprocess.PIPE)
        std_out = result.stdout.decode('utf-8')

        job_id = std_out.split("Submitted batch job ")[-1].replace("\n", "")
        
       
    if results != []:
        
        output_projection_csv = output_projection_csv.replace(".csv", f"_{mask_method}.csv")
        projection_records = {}
        # branch_and_tip_projection_records = {}
        for res in results:
            fn = os.path.abspath(res[0])
            proj_records = res[1]
            # brnch_tip_records = res[1]

            projection_records[fn] = proj_records
            # branch_and_tip_projection_records[fn] = brnch_tip_records

        proj_df = pd.DataFrame(projection_records).T.fillna(0)
        # proj_df_mask = pd.DataFrame(branch_and_tip_projection_records).T.fillna(0)

        proj_df.to_csv(output_projection_csv)
        # proj_df_mask.to_csv(output_projection_csv_tip_branch_mask)

        if projection_threshold != 0:
            output_projection_csv = output_projection_csv.replace(".csv",
                                                                "{}thresh.csv".format(projection_threshold))
            # output_projection_csv_tip_branch_mask = output_projection_csv_tip_branch_mask.replace(".csv",
            #                                                                                       "{}thresh.csv".format(
            #                                                                                           projection_threshold))

            proj_df_arr = proj_df.values
            proj_df_arr[proj_df_arr < projection_threshold] = 0
            proj_df = pd.DataFrame(proj_df_arr, columns=proj_df.columns, index=proj_df.index)
            proj_df.to_csv(output_projection_csv)

            # proj_df_mask_arr = proj_df_mask.values
            # proj_df_mask_arr[proj_df_mask_arr < projection_threshold] = 0
            # proj_df_mask = pd.DataFrame(proj_df_mask_arr, columns=proj_df_mask.columns, index=proj_df_mask.index)
            # proj_df_mask.to_csv(output_projection_csv_tip_branch_mask)

        if normalize_proj_mat:
            output_projection_csv = output_projection_csv.replace(".csv", "_norm.csv")
            # output_projection_csv_tip_branch_mask = output_projection_csv_tip_branch_mask.replace(".csv", "_norm.csv")

            proj_df = normalize_projection_columns_per_cell(proj_df)
            proj_df.to_csv(output_projection_csv)

            # proj_df_mask = normalize_projection_columns_per_cell(proj_df_mask)
            # proj_df_mask.to_csv(output_projection_csv_tip_branch_mask)




def console_script():
    module = ags.ArgSchemaParser(schema_type=IO_Schema)
    main(**module.args)

if __name__ == "__main__":
    module = ags.ArgSchemaParser(schema_type=IO_Schema)
    main(**module.args)
