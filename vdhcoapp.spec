%{?nodejs_find_provides_and_requires}
%global _enable_debug_package 0
%global debug_package %{nil}
%global __os_install_post /usr/lib/rpm/brp-compress %{nil}

%global commit0 42ac00507b1bd0952bbd12ebe64aac82d0f7b633
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global gver .git%{shortcommit0}

# Put here new versions of yarn
#https://github.com/yarnpkg/yarn/releases
%global y_ver 1.4.1

# We need said to gulp our Machine
%ifarch x86_64 
%global platform 64
%else
%global platform 32
%endif

Name: vdhcoapp
Summary: Companion application for Video DownloadHelper browser add-on 
Group: Applications/Internet
URL: https://github.com/mi-g/vdhcoapp
Version: 1.1.2
Release: 2%{?gver}%{?dist}
License: GPLv2
Source0: https://github.com/mi-g/vdhcoapp/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz
Source1: vdhcoapp-snapshot
Patch:   vdhcoapp.patch
Patch1:  fs-extra.patch
Patch2:  nodefix.patch
#-------------------------------------
BuildRequires: git 
BuildRequires: wget 
Requires: ffmpeg

%description
Companion application for Video DownloadHelper browser add-on.

%prep

%{S:1} -c %{commit0}
%setup -T -D -n %{name}-%{shortcommit0} 
%patch -p1
%patch1 -p1
%patch2 -p1

%build

# get yarn
wget -c https://github.com/yarnpkg/yarn/releases/download/v%{y_ver}/yarn-v%{y_ver}.tar.gz
tar xmzvf yarn-v%{y_ver}.tar.gz -C ~

# activate yarn
echo "export PATH=$PATH:~/yarn-v%{y_ver}/bin/:~/yarn-v%{y_ver}/lib/" >> ~/.bashrc

# get nvm

git clone git://github.com/creationix/nvm.git ~/nvm

# activate nvm

echo "source ~/nvm/nvm.sh" >> ~/.bashrc

source ~/.bashrc
nvm install 8.0.0
nvm use 8.0.0

# Begin the build
XCFLAGS="-g -O2 -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2" XLDFLAGS="-Wl,-z,relro"

~/yarn-v%{y_ver}/bin/yarn install
#~/yarn-v%{y_ver}/bin/yarn add brunch
#npm install

# Our Firefox multilib path
%ifarch x86_64 
sed -i 's|/usr/lib|/usr/lib64|g' gulpfile.js
sed -i 's|/usr/lib|/usr/lib64|g' app/native-autoinstall.js
sed -i 's|/usr/lib|/usr/lib64|g' assets/setup-linux-system.sh.ejs
%endif

# We need said a npm/yarn the path of binaries already installed... 
export PATH=$PATH:/usr/bin/:$PWD/node_modules/.bin/

# Now the installation
gulp build-linux-%{platform}


%install

install -Dm755 bin/net.downloadhelper.coapp-* %{buildroot}/%{_bindir}/vdhcoapp
install -Dm644 config.json %{buildroot}/%{_datadir}/vdhcoapp/config.json

%post
/usr/bin/vdhcoapp uninstall --system
/usr/bin/vdhcoapp install --system

%preun
/usr/bin/vdhcoapp uninstall --system

%files
%defattr(755, root, root)
%license LICENSE.txt
%{_bindir}/%{name}
%{_datadir}/%{name}/config.json

%changelog

* Thu Jan 25 2018 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.1.2-2
- Rebuilt for Firefox

* Thu Jan 11 2018 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.1.2-1
- Updated to 1.1.2-1

* Mon Dec 18 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.1.1-1
- Updated to 1.1.1-1

* Thu Dec 14 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.1.0-1
- initial build
