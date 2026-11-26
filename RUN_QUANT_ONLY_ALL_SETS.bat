@echo off
setlocal
cd /d "%~dp0"
if not defined FRAGPIPE_HOME set FRAGPIPE_HOME=C:\FragPipe\FragPipe-24.0
set FP=%FRAGPIPE_HOME%
set JAVA_HOME=%FP%\jre
set OUT=results_large\search_ALL_SETS
if not exist "%OUT%" mkdir "%OUT%"
echo Start: %date% %time% > "%OUT%\run_times_quant_only.txt"
echo FragPipe quantification (no search) ALL_SETS is running. Progress is written to %OUT%\run_log_quant_only.txt
echo Do not close this window.
call "%FP%\bin\fragpipe.bat" --headless --workflow "%~dp0config\MOSAIC_TMT10_variants_quant_only.workflow" --manifest "%~dp0config\ALL_SETS.fp-manifest" --workdir "%~dp0%OUT%" --config-tools-folder "%FP%\tools" --ram 24 --threads 18 > "%OUT%\run_log_quant_only.txt" 2>&1
echo End: %date% %time% >> "%OUT%\run_times_quant_only.txt"
echo.
echo FINISHED. See %OUT%\run_log_quant_only.txt
pause
