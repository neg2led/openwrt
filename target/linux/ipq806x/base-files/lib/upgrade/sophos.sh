. /lib/functions.sh

# By default, the u-boot in a Sophos APX device will validate both the main
# and backup FIT images for a valid signature before booting; in the event
# that both images fail, a custom u-boot app will attempt to restore the OEM
# firmware from a Sophos Firewall appliance on the same network.

sophos_upgrade_prepare_apx() {
	local ubidev="$( nand_find_ubi rootfs )"

	# make sure u-boot image signing verification is disabled
	fw_setenv verify no || exit 1

	# Set bootdelay=3 if OEM firmware has left it set to 0
	[ "$( fw_printenv -n bootdelay )" = '0' ] && fw_setenv bootdelay '3' || true

	# back up bootcmd if not done, set new bootcmd
	[ "$( fw_printenv -n oem_bootcmd )" ] || fw_setenv oem_bootcmd "$( fw_printenv -n bootcmd )"
	fw_setenv bootcmd 'run ubiboot; run flashtool; reset' || exit 1

	# clear image_backup, config, and download volumes if present
	ubirmvol /dev/$ubidev -N image_backup &> /dev/null || true
	ubirmvol /dev/$ubidev -N config &> /dev/null || true
	ubirmvol /dev/$ubidev -N download &> /dev/null || true
}
