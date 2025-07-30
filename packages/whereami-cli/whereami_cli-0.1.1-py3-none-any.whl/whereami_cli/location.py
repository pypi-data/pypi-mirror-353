#!/usr/bin/env python3
import geocoder
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from datetime import datetime

def get_current_location():
    console = Console()
    try:
        with console.status("[bold green]正在获取位置信息...") as status:
            # 获取当前位置
            location = geocoder.ip('me')
            
            if location.ok:
                lat, lng = location.latlng
                
                # 创建表格
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("信息", style="cyan")
                table.add_column("详情", style="green")
                
                table.add_row("📍 纬度", f"{lat}")
                table.add_row("📍 经度", f"{lng}")
                table.add_row("🏠 地址", f"{location.address}")
                table.add_row("⏰ 时间", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
                # 创建面板
                panel = Panel(
                    table,
                    title="[bold yellow]位置信息[/bold yellow]",
                    border_style="blue",
                    padding=(1, 2)
                )
                
                # 打印面板
                console.print(panel)
                
                # 添加高德地图链接
                map_url = f"https://uri.amap.com/marker?position={lng},{lat}&name=当前位置"
                console.print(f"\n[bold blue]🗺️ 在高德地图中查看:[/bold blue] [link={map_url}]{map_url}[/link]")
                
            else:
                console.print("[bold red]❌ 无法获取位置信息，请检查网络连接。[/bold red]")
                sys.exit(1)
                
    except Exception as e:
        console.print(f"[bold red]❌ 发生错误: {str(e)}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    get_current_location() 