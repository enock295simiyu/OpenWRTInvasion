import logging
from time import sleep

from connectors.telnet import SshTelnetConnector

logger = logging.getLogger("netmiko")

def install_openwrt(username='root',password='',router_address='',openwrt_download_link='http://downloads.openwrt.org/releases/24.10.2/targets/ramips/mt76x8/openwrt-24.10.2-ramips-mt76x8-xiaomi_mi-router-4c-squashfs-sysupgrade.bin'):
    logger.info('Installing OpenWRT on xiami mi router...')
    connector = SshTelnetConnector(
        params={
            'username': username,
            'password': password,
            # 'port':22
        },
        addresses=[router_address],
    )
    logger.info(f'Changing the directory to /tmp')


    response=connector.exec_command("cd /tmp")

    logger.info(response[0])
    logger.info(f'Downloading openwrt bin file from {openwrt_download_link}')
    download_response=connector.exec_command(f'wget -O openwrt.bin {openwrt_download_link}')
    logger.info(download_response[0])
    logger.info('Installing OpenWRT on xiaomi mi router. The router take will couple of minutes and will be restarted to OpenWrt. Do not switch off the router during this period.')
    sleep(5)
    install_response=connector.exec_command("mtd -r write /tmp/openwrt.bin OS1")
    logger.info(install_response)

if __name__ == '__main__':
    install_openwrt(username='root',password='',router_address='172.25.0.1',openwrt_download_link='https://openwrt.org/_detail/media/xiaomi/mi_router_4c.png?id=toh%3Axiaomi%3Axiaomi_mi_router_4c')