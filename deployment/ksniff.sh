(
wget -P /install https://github.com/eldadru/ksniff/releases/download/v1.6.2/ksniff.zip &&
unzip /install/ksniff.zip -d /install &&
sed -i 's/--short=true //' /install/Makefile &&
pwd &&
ls &&
make -C /install install
)