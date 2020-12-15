$PY_VERSION='3.6'
$BASE_DIR = 'dependencies'
$PKG_DIR = $BASE_DIR + '/python'


Remove-Item -Recurse -Force $PKG_DIR
New-Item -ItemType Directory -Name $PKG_DIR

# make sure python is actually python 3.6
python -m pip install -r requirements.txt --no-deps -t $PKG_DIR
New-Item -ItemType File -Name "__init__.py" -Path $PKG_DIR
Copy-Item -Recurse -Path '..\..\common\*' -Destination $PKG_DIR