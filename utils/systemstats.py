import asyncio
import psutil

def scale_bytes(bytes):

    factor = 1024
    for unit in ["", "K", "M", "G"]:
        if bytes < factor:
            return f'{bytes:.2f}{unit}B'
        bytes /= factor

async def get_system_stats():

    # CPU
    cpu_usage = psutil.cpu_percent()
    await asyncio.sleep(0.2)
    cpu_usage = psutil.cpu_percent()
    cpu_cores = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()[0]

    # RAM
    ram = psutil.virtual_memory()
    ram_percent = ram.percent
    ram_free = scale_bytes(ram.free)
    ram_total =scale_bytes(ram.total)

    # DISK
    disk_usage = psutil.disk_io_counters()
    disk_read = disk_usage[2]
    disk_write = disk_usage[3]
    await asyncio.sleep(0.5)
    disk_usage = psutil.disk_io_counters()
    disk_read = scale_bytes((disk_usage[2] - disk_read)*2)
    disk_write = scale_bytes((disk_usage[3] - disk_write)*2)

    # NETWORK
    net_usage = psutil.net_io_counters()
    net_recv = net_usage[1]
    net_send = net_usage[0]
    await asyncio.sleep(0.5)
    net_usage = psutil.net_io_counters()
    net_recv = scale_bytes((net_usage[1] - net_recv)*2)
    net_send = scale_bytes((net_usage[0] - net_send)*2)

    # CPU
    percent = round(cpu_usage/10)
    cpu_bar = ''
    for i in range(1, 10):
        cpu_bar += ('#' if i <= percent else '-')
    cpu_usage = f'Usage: |{cpu_bar}| {cpu_usage}%'
    cpu_cores = f'Cores: {cpu_cores}'
    cpu_freq = f'Frequency: {cpu_freq/1000}Ghz'
    cpu = f'**CPU:**\n{cpu_usage}\n{cpu_cores}\n{cpu_freq}'

    # RAM
    percent = round(ram_percent/10)
    ram_bar = ''
    for i in range(1, 10):
        ram_bar += ('#' if i <= percent else '-')
    ram_usage = f'Usage: |{ram_bar}| {ram_percent}%'
    ram_free = f'Free: {ram_free}'
    ram_total = f'Total: {ram_total}'
    ram = f'**RAM:**\n{ram_usage}\n{ram_free}\n{ram_total}'

    # DISK
    disk_read = f'Read: {disk_read}/s'
    disk_write = f'Write: {disk_write}/s'
    disk = f'**DISK:**\n{disk_read}\n{disk_write}'

    # NETWORK
    net_recv = f'Download: {net_recv}/s'
    net_send = f'Upload: {net_send}/s'
    net = f'**NETWORK:**\n{net_recv}\n{net_send}'

    return f'\n{cpu}\n\n{ram}\n\n{disk}\n\n{net}'