import sys

MIN_PYTHON = (3, 7)
assert sys.version_info >= MIN_PYTHON, f"requires Python {'.'.join([str(n) for n in MIN_PYTHON])} or newer"

from os import listdir, getcwd, system, replace
from os.path import isfile, isdir, join
import re
from shutil import rmtree
from subprocess import Popen

cwd = getcwd()

inferenceScript = join(cwd, 'BackgroundMattingV2', 'inference_video.py')
modelPath = join('Models', 'PyTorch', 'pytorch_resnet50.pth')

if not isfile(inferenceScript):
    print(f'Inference script missing, expected to exist at \'{inferenceScript}\'')
    print('Check your working directory')
    sys.exit(1)

if not isfile(modelPath):
    print(f'Model missing, expected to exist at \'{modelPath}\'')
    print('Check your working directory')
    sys.exit(1)

if len(sys.argv) == 1:
    print("Specify input directory")
    sys.exit(1)

inputDir = sys.argv[1]

if not isdir(inputDir):
    print(f'{inputDir} is not a directory')

files = listdir(inputDir)

videoFiles = []

for file in files:
    fileMatch = re.match(r"(?P<base>.*)\.(?P<ext>mp4|mov|avi|mkv)$", file)
    if fileMatch:
        base = fileMatch.group('base')
        ext = fileMatch.group('ext')
        print(f'Found video file {base}.{ext}')
        bgFile = f'{base}.png'
        if isfile(join(inputDir, bgFile)):
            videoFiles.append({
                'video': file,
                'bg': bgFile,
                'base': base
            })
        else:
            print(f'Missing background image \'{bgFile}\', skipping this video!')

totalFiles = len(videoFiles)
currentFile = 0
outputBase = join(inputDir, '__tmp')
for videoDict in videoFiles:
    fileNumber = currentFile + 1;
    print(f'Processing file {fileNumber} of {totalFiles}, {videoDict["base"]}')
    videoFile = join(inputDir, videoDict['video'])
    bgFile = join(inputDir, videoDict['bg'])

    outputDir = join(outputBase, videoDict['base'])

    print(f'Outputting to temporary dir: {outputDir}')

    if isdir(outputDir):
        print(f'Cleaning temporary output directory: {outputDir}')
        rmtree(outputDir)

    proc = Popen([
        'python', inferenceScript,
        '--model-type', 'mattingrefine',
        '--model-backbone', 'resnet50',
        '--model-checkpoint', modelPath,
        '--model-refine-mode', 'full',
        '--video-src', videoFile,
        '--video-bgr', bgFile,
        '--output-dir', outputDir,
        '--output-types', 'pha',
        '--output-format', 'video'])

    proc.wait()

    tmpVideo = join(outputDir, 'pha.mp4')
    outputVideo = join(inputDir, f'{videoDict["base"]}_mask.mp4')


    if isfile(tmpVideo):
        replace(tmpVideo, outputVideo)

    currentFile += 1

print("Done processing")
print(f'Cleaning temporary output directory: {outputBase}')
rmtree(outputBase)
