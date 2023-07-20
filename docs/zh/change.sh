echo $1
sudo kill -9 $1
mkdocs build
nohup mkdocs serve -a 0.0.0.0:8021 > ctf-wiki.log 2>&1 &
