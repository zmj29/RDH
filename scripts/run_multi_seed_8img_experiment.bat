@echo off
setlocal

cd /d "%~dp0\.."

if not defined CNNP_ENV set CNNP_ENV=cnnp37

if defined CONDA_ACTIVATE (
    call "%CONDA_ACTIVATE%" "%CNNP_ENV%"
) else (
    call conda activate "%CNNP_ENV%"
)
if errorlevel 1 (
    echo Failed to activate conda environment: %CNNP_ENV%
    echo Set CNNP_ENV to the target environment name, or set CONDA_ACTIVATE to activate.bat.
    exit /b 1
)

set IMAGE_DIR=.\datasets\extended_test_images_8
set OUTPUT_ROOT=.\results\multi_seed_8img

if not exist "%IMAGE_DIR%" (
    echo Image directory not found: %IMAGE_DIR%
    echo Please prepare the 8 test images first.
    exit /b 1
)

echo Running seed 20260406...
python data_processing\run_cnnp_batch.py ^
  --image-dir "%IMAGE_DIR%" ^
  --seed 20260406 ^
  --results-csv "%OUTPUT_ROOT%\seed_20260406\cnnp_psnr_results.csv" ^
  --per-image-csv "%OUTPUT_ROOT%\seed_20260406\per_image_results.csv" ^
  --average-csv "%OUTPUT_ROOT%\seed_20260406\average_results.csv" ^
  --trend-csv "%OUTPUT_ROOT%\seed_20260406\payload_psnr_trend.csv" ^
  --gap-csv "%OUTPUT_ROOT%\seed_20260406\mode_gap_comparison.csv" ^
  --env-info "%OUTPUT_ROOT%\seed_20260406\environment_info.txt" ^
  --logs-dir "%OUTPUT_ROOT%\seed_20260406\logs"
if errorlevel 1 exit /b 1

echo Running seed 20260407...
python data_processing\run_cnnp_batch.py ^
  --image-dir "%IMAGE_DIR%" ^
  --seed 20260407 ^
  --results-csv "%OUTPUT_ROOT%\seed_20260407\cnnp_psnr_results.csv" ^
  --per-image-csv "%OUTPUT_ROOT%\seed_20260407\per_image_results.csv" ^
  --average-csv "%OUTPUT_ROOT%\seed_20260407\average_results.csv" ^
  --trend-csv "%OUTPUT_ROOT%\seed_20260407\payload_psnr_trend.csv" ^
  --gap-csv "%OUTPUT_ROOT%\seed_20260407\mode_gap_comparison.csv" ^
  --env-info "%OUTPUT_ROOT%\seed_20260407\environment_info.txt" ^
  --logs-dir "%OUTPUT_ROOT%\seed_20260407\logs"
if errorlevel 1 exit /b 1

echo Running seed 20260408...
python data_processing\run_cnnp_batch.py ^
  --image-dir "%IMAGE_DIR%" ^
  --seed 20260408 ^
  --results-csv "%OUTPUT_ROOT%\seed_20260408\cnnp_psnr_results.csv" ^
  --per-image-csv "%OUTPUT_ROOT%\seed_20260408\per_image_results.csv" ^
  --average-csv "%OUTPUT_ROOT%\seed_20260408\average_results.csv" ^
  --trend-csv "%OUTPUT_ROOT%\seed_20260408\payload_psnr_trend.csv" ^
  --gap-csv "%OUTPUT_ROOT%\seed_20260408\mode_gap_comparison.csv" ^
  --env-info "%OUTPUT_ROOT%\seed_20260408\environment_info.txt" ^
  --logs-dir "%OUTPUT_ROOT%\seed_20260408\logs"
if errorlevel 1 exit /b 1

echo Aggregating multi-seed results...
python data_processing\aggregate_multi_seed_results.py --input-root "%OUTPUT_ROOT%"
if errorlevel 1 exit /b 1

echo Done.
echo Summary CSV: %OUTPUT_ROOT%\aggregated\mode_payload_summary.csv
echo Image summary CSV: %OUTPUT_ROOT%\aggregated\mode_payload_image_summary.csv

endlocal
