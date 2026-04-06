# CNN-Prediction-Based-Reversible-Data-Hiding


## Author: 

   #### Runwen Hu and Shijun Xiang

   School of Information Science and Technology/School of Cyber Security, Jinan University
   Guangzhou, China



## Description:

This version can only calculate the PSNR of images by using the proposed CNN-based predictor (CNNP) with expansion embedding and histogram shifting. The working environment is Windows 10, Python 3.7, PyTorch 1.6.0, and MATLAB 2019a. The work is based on the paper:

   #### R. Hu and S. Xiang, "CNN Prediction Based Reversible Data Hiding," in IEEE Signal Processing Letters, vol. 28, pp. 464-468, 2021, doi: 10.1109/LSP.2021.3059202.



## Folder description :

   "standard_test_images":  This folder contains four standard images used in this paper. Other images come from ImageNet.

   "model":                          This folder contains the proposed CNN-based predictor.

   "model_parameter":         This folder contains the parameter of the proposed CNN-based predictor.

   "data_processing":        This folder contains batch experiment scripts for exporting per-image results, average tables, logs, and charts used in the thesis.

   "results/paper_experiment_2026-04-06":  This folder contains the exported thesis experiment results, including CSV files, environment information, logs, and chart images.


## Usage:

#### python main.py [size] [model] [folder] [length] 

   size:                 The size of the images, which is set to 512*512 in this letter.
   
   model:             The saved model parameters. 
   
   folder:              The place of the image to be predicted.
   
   length:             The length of the data to be hidden.


After using this program, the PSNR of the watermarked image by using the proposed CNNP-based reversible data hiding method will appear.

## Example:

### (1)For histogram shifting:

   #### python main.py -size 512 512 -model .\model_parameter\model_state.pth -folder .\standard_test_images -mode histogram_shifting -length 10000


### (2)For expansion embedding:

   #### python main.py -size 512 512 -model .\model_parameter\model_state.pth -folder .\standard_test_images -mode expansion_embedding -length 10000


## Thesis Scripts and Results

### Batch export scripts

Run the thesis-oriented batch experiment exporter from the repository root:

#### python data_processing\run_cnnp_batch.py

Generate thesis chart images from the exported CSV files:

#### python data_processing\plot_cnnp_results.py

### Stored experiment results

The repository includes one structured result set under:

#### .\results\paper_experiment_2026-04-06

This result folder contains:

- per-image result tables
- average result tables
- environment information
- raw logs for each mode and payload
- chart source CSV files
- generated chart PNG files









