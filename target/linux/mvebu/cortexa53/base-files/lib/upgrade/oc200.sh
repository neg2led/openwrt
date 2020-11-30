platform_do_prepare_oc200() {
	if ! grep -q /data /proc/mounts; then
		mkdir -p /data
		mount /dev/mmcblk0p4 /data
	fi
}

platform_do_upgrade_oc200() {
	platform_do_prepare_oc200
	platform_copy_config_oc200

	grep -q /dev/mmcblk0p4 /proc/mounts && umount /data
	grep -q /dev/root /proc/mounts && umount /

	dd if="$1" of=/dev/mmcblk0 bs=512 seek=896
	sync

	umount -l /tmp
	umount -l /dev
}

platform_copy_config_oc200() {
	if [ -f "$UPGRADE_BACKUP" ]; then
		cp -f "$UPGRADE_BACKUP" "/data/$BACKUP_FILE"
	fi
}
