# py-cmus-bouncer
Simple headless keypress-to-cmus-remote-command script, intended for use on raspberry pi

## dependencies

* cmus
```shell
sudo apt-get install cmus
```

* pycmus
```shell
sudo pip install pycmus
```

Sample rpi setup to run headless on boot (on Ubuntu Mate 16.04)

- Enable login to terminal
```shell
echo '#!/bin/bash
# Call with either enable or disable as first parameter
if [[ "$1" == 'enable' || "$1" == 'disable' ]]; then
    sudo systemctl set-default multi-user.target --force
    sudo systemctl $1 lightdm.service --force
    sudo systemctl $1 graphical.target --force
    sudo systemctl $1 plymouth.service --force
else
    echo Call with either "enable" or "disable" as first parameter.
fi
' > ~/bootgui.sh
chmod +x ~/bootgui.sh

~/bootgui.sh enable
```

- Enable autologin
```shell
sudo mkdir /etc/systemd/system/getty@tty1.service.d
sudo emacs -nw /etc/systemd/system/getty@tty1.service.d/autologin.conf

(in file, write:)
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin YOURUSERNAMEHERE --noclear %I 38400 linux
```

- Append program invocation to .profile
```shell
echo 'screen -S whitenoise /home/user/whitenoise/whitenoise.py -d /home/user/Music/WhiteNoise/' >> ~/.profile
```

