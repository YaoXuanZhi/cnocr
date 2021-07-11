@echo off
chcp 65001 > nul

title cnstd-train

set MXNET_CPU_WORKER_NTHREADS=2
set DATA_ROOT_DIR=data/sample-data
set REC_DATA_ROOT_DIR=data/sample-data-lst
set IMAGES_DIR=examples

:: `EMB_MODEL_TYPE` 可取值：['conv', 'conv-lite-rnn', 'densenet', 'densenet-lite']
set EMB_MODEL_TYPE=densenet-lite
:: `SEQ_MODEL_TYPE` 可取值：['lstm', 'gru', 'fc']
set SEQ_MODEL_TYPE=gru
set MODEL_NAME=%EMB_MODEL_TYPE%-%SEQ_MODEL_TYPE%

@REM ------------------------------------------------------------------

:do

cls

echo 1: gen_lst

echo 2: gen_rec

echo 3: train

echo 4: evaluate

echo 5: predict

echo 6: package

echo 7: upload

set /p o=

if %o%==1 goto gen_lst

if %o%==2 goto gen_rec

if %o%==3 goto train

if %o%==4 goto evaluate

if %o%==5 goto predict

if %o%==6 goto package

if %o%==7 goto upload

goto end

@REM ------------------------------------------------------------------

:: 产生 *.lst 文件
:gen_lst
	echo python scripts/im2rec.py --list --num-label 20 --chunks 1 --train-idx-fp %DATA_ROOT_DIR%/train.txt --test-idx-fp %DATA_ROOT_DIR%/test.txt --prefix %REC_DATA_ROOT_DIR%/sample-data
	python scripts/im2rec.py --list --num-label 20 --chunks 1 --train-idx-fp %DATA_ROOT_DIR%/train.txt --test-idx-fp %DATA_ROOT_DIR%/test.txt --prefix %REC_DATA_ROOT_DIR%/sample-data

pause
GOTO do

:: 利用 *.lst 文件产生 *.idx 和 *.rec 文件。
:: 真正的图片文件存储在 `examples` 目录，可通过 `--root` 指定。
:gen_rec
	echo python scripts/im2rec.py --pack-label --color 1 --num-thread 1 --prefix %REC_DATA_ROOT_DIR% --root %IMAGES_DIR%
	python scripts/im2rec.py --pack-label --color 1 --num-thread 1 --prefix %REC_DATA_ROOT_DIR% --root %IMAGES_DIR%

pause
GOTO do

:: 训练模型
:train
	python scripts/cnocr_train.py --gpu 0 --emb_model_type %EMB_MODEL_TYPE% --seq_model_type %SEQ_MODEL_TYPE% --optimizer adam --epoch 20 --lr 1e-4 --train_file %REC_DATA_ROOT_DIR%/sample-data_train --test_file %REC_DATA_ROOT_DIR%/sample-data_test

pause
GOTO do

:: 在测试集上评估模型，所有badcases的具体信息会存放到文件夹 `evaluate/%MODEL_NAME%` 中
:evaluate
	python scripts/cnocr_evaluate.py --model-name %MODEL_NAME% --model-epoch 1 -v -i %DATA_ROOT_DIR%/test.txt --image-prefix-dir examples --batch-size 128 -o evaluate/%MODEL_NAME%

pause
GOTO do

:predict
	python scripts/cnocr_predict.py --model_name %MODEL_NAME% --file examples/rand_cn1.png

pause
GOTO do

:package
	python setup.py sdist bdist_wheel

pause
GOTO do

:upload
	set VERSION=1.2.2
	python -m twine upload  dist/cnocr-%VERSION% --verbose

pause
GOTO do

:end
pause
GOTO :eof