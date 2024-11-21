function hook() {
    bypass_korea();
    bypass_testKeys();
    bypass_superUser();
    bypass_emulator_goldFish();
    bypass_adbEnabled();
    bypass_VPN_tun0_ppp0();
    bypass_proxy();
}

function bypass_korea() {
    Java.perform(function () {
        var locale = Java.use("java.util.Locale").getLanguage.overload();
            locale.implementation = function () {
                return "ko";
            };
    });
}

function bypass_testKeys() {
    Java.perform(function () {
        var contains = Java.use("java.lang.String").contains.overload("java.lang.CharSequence");
            contains.implementation = function (key) {
                if (key == "test-keys") {
                    return false;
                }
                return contains.call(this, key);
            };
    });
}

function bypass_superUser() {       
    Java.perform(function () {
        var fileClass = Java.use("java.io.File").$init.overload("java.lang.String");
            fileClass.implementation = function (path) {
                if (path == "/system/app/Superuser.apk") {
                    return fileClass.call(this, "/nothing");
                }
                return fileClass.call(this, path);
            };
    });
}

function bypass_emulator_goldFish() {
    Java.perform(function () {
        var indexof = Java.use("java.lang.String").indexOf.overload("java.lang.String");
            indexof.implementation = function (gold) {
                if (gold == "goldfish") {
                    return Java.use("int").$new(-1);
                }
                return indexof.call(this, gold);
            };
    });
}

function bypass_adbEnabled() {
    Java.perform(function () {
        var Secure = Java.use("android.provider.Settings$Secure");
        var getInt = Secure.getInt.overload("android.content.ContentResolver", "java.lang.String", "int");
            getInt.implementation = function (resolver, name, def) {
                if (name == "adb_enabled") {
                    return Java.use("int").$new(0);
                }
                return getInt.call(this, resolver, name, def);
            };
    });
}

function bypass_VPN_tun0_ppp0() {
    Java.perform(function () {
        var equals = Java.use("java.lang.String").equals.overload("java.lang.Object");
            equals.implementation = function (vpn) {
                if (vpn == "tun0" || vpn == "ppp0") {
                    return false;
                }
                return equals.call(this, vpn);
            };
    });
}

function bypass_proxy() {
    Java.perform(function () {
        var system = Java.use("java.lang.System");
        var getProperty = system.getProperty.overload("java.lang.String");
            getProperty.implementation = function (proxy) {
                if (proxy == "http.proxyHost" || proxy == "http.proxyPort") {
                    return null;
                }
                return getProperty.call(system, proxy);
            };
    });
}

hook();