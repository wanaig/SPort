"""Linux-specific implementations of the SPort platform layer.

Provides:

* :class:`Autostart` — XDG autostart ``~/.config/autostart/<app_id>.desktop``.
* :class:`LinuxNotifier` — desktop notifications via ``plyer`` (libnotify).
* :func:`get_system_registry` — Linux system processes and accounts.

Linux has no PPL equivalent. Other users' processes may still be hidden from
psutil when SPort runs unprivileged; callers should recommend ``sudo`` for
full visibility, same as the Windows "run as Administrator" hint.
"""
from __future__ import annotations

import os
import sys
from typing import Any, Dict, Optional

from ._common import AutostartController, Notifier as BaseNotifier, SystemProcessRegistry

PLATFORM_NAME = "linux"


# ---------------------------------------------------------------------------
# Autostart (XDG)
# ---------------------------------------------------------------------------
class Autostart(AutostartController):
    AUTOSTART_DIR = os.path.expanduser("~/.config/autostart")

    @property
    def desktop_path(self) -> str:
        return os.path.join(self.AUTOSTART_DIR, f"{self.app_id}.desktop")

    def _build_desktop(self) -> str:
        if getattr(sys, "frozen", False):
            exec_cmd = f'"{sys.executable}"'
        else:
            script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tray.py"))
            exec_cmd = f'"{sys.executable}" "{script}"'
        return (
            "[Desktop Entry]\n"
            "Type=Application\n"
            f"Name={self.app_name}\n"
            f"Comment={self.app_name} — Real-time port monitor\n"
            f"Exec={exec_cmd} --silent\n"
            "Terminal=false\n"
            "X-GNOME-Autostart-enabled=true\n"
            "Categories=Utility;Network;Monitor;\n"
        )

    def is_enabled(self) -> bool:
        return os.path.exists(self.desktop_path)

    def set_enabled(self, enabled: bool) -> bool:
        if not enabled:
            try:
                os.remove(self.desktop_path)
            except FileNotFoundError:
                pass
            return True
        try:
            os.makedirs(self.AUTOSTART_DIR, exist_ok=True)
            with open(self.desktop_path, "w", encoding="utf-8") as f:
                f.write(self._build_desktop())
            return True
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Notifications (plyer -> libnotify)
# ---------------------------------------------------------------------------
class Notifier(BaseNotifier):
    def __init__(self, app_id: str, app_name: str):
        super().__init__(app_id, app_name)
        try:
            from plyer import notification  # type: ignore
            self._notification = notification
            self._available = True
        except ImportError:
            self._notification = None
            self._available = False

    def notify(self, title: str, message: str, icon_path: Optional[str] = None) -> bool:
        if not self._available:
            return False
        try:
            self._notification.notify(
                title=title,
                message=message,
                app_name=self.app_name,
                app_icon=icon_path or "",
                timeout=5,
            )
            return True
        except Exception:
            return False


# ---------------------------------------------------------------------------
# System process registry
# ---------------------------------------------------------------------------
LINUX_SYSTEM_PROCESSES = {
    # Init / service management
    "systemd", "systemd-journald", "systemd-logind", "systemd-udevd",
    "systemd-networkd", "systemd-resolved", "systemd-timesyncd",
    "systemd-userdbd", "systemd-tmpfiles", "systemd-coredump",
    "systemd-machine-id-setup", "systemd-sysctl", "systemd-modules-load",
    "systemd-update-utmp", "systemd-remount-fs",
    # Network
    "NetworkManager", "wpa_supplicant", "dhclient", "dhcpcd",
    "connmand", "iwd", "hostapd", "dnsmasq",
    # Audio
    "pulseaudio", "pipewire", "wireplumber", "pipewire-pulse",
    # Display / session
    "Xorg", "Xwayland", "wayland", "gnome-shell", "kwin", "kwin_wayland",
    "sddm", "gdm", "gdm-wayland-session", "gdm-x-session", "lightdm",
    "slick-greeter", "xfce4-session", "mate-session", "cinnamon-session",
    "lxsession", "lxqt-session", "enlightenment", "sway",
    # D-Bus / policy
    "dbus-daemon", "dbus-broker", "dbus-broker-launcher",
    "polkitd", "polkit-gnome-authentication-agent-1",
    "polkit-kde-authentication-agent-1",
    # Desktop helpers
    "at-spi-bus-launcher", "at-spi2-registryd",
    "gvfsd", "gvfs-udisks2-volume-monitor", "gvfs-gphoto2-volume-monitor",
    "gvfs-mtp-volume-monitor", "gvfs-afc-volume-monitor",
    "xdg-desktop-portal", "xdg-desktop-portal-gtk",
    "xdg-desktop-portal-kde", "xdg-desktop-portal-gnome",
    "xdg-document-portal", "xdg-permission-store",
    "dconf-service", "gconfd-2",
    # Bluetooth / hardware
    "bluetoothd", "blueman-manager", "boltd", "upowerd",
    # Printing
    "cupsd", "cups-browsed", "cups-notifyd",
    # Thermal / power
    "thermald", "power-profiles-daemon", "tlp", "auto-cpufreq",
    # Snap / flatpak
    "snapd", "snap-confine", "flatpak-session-helper", "flatpak-portal",
    "flatpak-system-helper", "flatpak-oci-authenticator",
    # Logind helpers
    "accounts-daemon", "colord", "rtkit-daemon", "switcheroo-control",
    # Security
    "firewalld", "ufw", "apparmor", "auditd", "fail2ban-server",
    "clamd", "clamav-milter", "freshclam",
    # Log / cron
    "cron", "crond", "anacron", "rsyslogd", "syslog-ng",
    "logrotate", "logwatch",
    # Update
    "packagekitd", "fwupd", "unattended-upgrade", "unattended-upgrades-shutdown",
    # Entropy
    "haveged", "rngd",
    # Snapshots
    "snapperd", "btrfs-cleaner", "btrfs-transacti",
    # mDNS / avahi
    "avahi-daemon", "avahi-autoipd",
    # SSH
    "sshd",
    # Containers
    "containerd", "containerd-shim", "containerd-shim-runc-v2",
    "dockerd", "docker-proxy", "docker-init",
    "podman", "conmon", "crun", "runc",
    # VPN
    "openvpn", "wireguard", "wg-quick", "strongswan", "charond",
    # Time
    "chronyd", "ntpd", "systemd-timedated",
    # DNS
    "named", "unbound", "systemd-resolved",
    # Mail
    "postfix", "dovecot", "exim4", "sendmail",
    # Web
    "nginx", "apache2", "httpd", "lighttpd", "caddy",
    # Database (when system-managed)
    "mysqld", "mariadbd", "postgres", "redis-server", "mongod",
    # Backup
    "borg", "restic", "duplicity",
    # Locales
    "locale-gen",
    # Filesystem
    "udisksd", "udisks-glue",
}

LINUX_SYSTEM_USERS = {
    "root",
    "systemd-network", "systemd-resolve", "systemd-timesync",
    "systemd-coredump", "_apt", "messagebus",
    "daemon", "bin", "sys", "sync", "games", "man", "lp", "mail",
    "news", "uucp", "proxy", "www-data", "backup", "list", "irc",
    "gnats", "nobody",
    "Debian-snmp", "_chrony", "polkitd", "rtkit",
    "avahi-autoipd", "avahi", "usbmux", "nm-openvpn",
    "sshd", "cups-pk-helper", "geoclue", "pulse", "pipelight",
    "snapd-range-524288-root", "snap_daemon",
    "fwupd-refresh", "dnsmasq",
    "colord", "gnome-initial-setup",
    "tcpdump", "Debian-snmpd",
    "redis", "postgres", "mysql", "mongodb",
    "nginx", "www", "http",
    "kernoops", "rdma", "tss",
    "_runtimer", "_chrony", "systemd-user",
    "nm-openvpn", "nm-openvpn-handler",
    "nm-strongswan", "nm-l2tpd", "nm-pptp",
    "libvirt-dnsmasq", "libvirt-qemu", "libvirt",
    "dockerroot",
    "clamav", "clamav-milter",
    "nslcd", "epmd", "rabbitmq",
    "_gvm", "gvm", "nessusd",
    "flatpak", "snapd",
}


def get_system_registry() -> SystemProcessRegistry:
    return SystemProcessRegistry(LINUX_SYSTEM_PROCESSES, LINUX_SYSTEM_USERS)


def get_protected_process_info(pid: int) -> Optional[Dict[str, Any]]:
    """No PPL concept on Linux; psutil covers everything reachable."""
    return None
