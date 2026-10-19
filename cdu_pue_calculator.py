#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CDU and PUE Calculator for Liquid Cooling Data Centers
液冷数据中心 CDU 和 PUE 计算工具

This script calculates the required coolant flow rate, heat load, and estimated PUE
for a cold plate liquid cooling system based on IT power, coolant properties,
temperature difference, and auxiliary power consumption.

该脚本根据 IT 功率、冷却液性质、温差和辅助功率消耗，
计算冷板式液冷系统所需的冷却液流量、散热负荷和估算 PUE。

Usage:
    python cdu_pue_calculator.py --it_power 100 --specific_heat 4.18 --density 1000 --delta_t 5 --aux_power 10

Author: Cyberpunk Engineer (赛博朋克工程师)
Version: 1.0
Date: 2026-10-12
"""

import argparse
import sys
from typing import Tuple

# ANSI color codes for cyberpunk terminal style
# 赛博朋克终端样式的 ANSI 颜色代码
class colors:
    HEADER = '\033[95m'      # 洋红 / Magenta
    BLUE = '\033[94m'        # 蓝色 / Blue
    CYAN = '\033[96m'        # 青蓝 / Cyan
    GREEN = '\033[92m'       # 绿色 / Green
    YELLOW = '\033[93m'      # 黄色 / Yellow
    RED = '\033[91m'         # 红色 / Red
    BOLD = '\033[1m'         # 加粗 / Bold
    UNDERLINE = '\033[4m'    # 下划线 / Underline
    END = '\033[0m'          # 结束颜色 / End color
    BACKGROUND = '\033[40m'  # 黑色背景 / Black background


def calculate_flow_rate(
    power_it: float,
    specific_heat: float,
    density: float,
    delta_t: float
) -> Tuple[float, float, float]:
    """
    Calculate coolant volumetric flow rate based on heat load and temperature difference.
    根据热负荷和温差计算冷却液体积流量。

    Args:
        power_it: IT equipment total power in kW (IT 设备总功率，单位 kW)
        specific_heat: Coolant specific heat capacity in kJ/(kg·K) (冷却液比热容，单位 kJ/(kg·K))
        density: Coolant density in kg/m³ (冷却液密度，单位 kg/m³)
        delta_t: Temperature difference between supply and return in K or °C (供回水温差，单位 K 或 °C)

    Returns:
        Tuple of (flow_rate_m3_s, flow_rate_L_s, flow_rate_m3_h)
        (流量 m³/s, 流量 L/s, 流量 m³/h)
    """
    # Convert power from kW to kJ/s (1 kW = 1 kJ/s)
    # 将功率从 kW 转换为 kJ/s（1 kW = 1 kJ/s）
    heat_load_kj_s = power_it  # Since 1 kW = 1 kJ/s

    # Calculate mass flow rate: m_dot = Q / (c * ΔT)
    # 计算质量流量：m_dot = Q / (c * ΔT)
    if specific_heat <= 0 or delta_t <= 0:
        raise ValueError("Specific heat and delta_t must be positive values.")

    mass_flow_rate_kg_s = heat_load_kj_s / (specific_heat * delta_t)  # kg/s

    # Calculate volumetric flow rate: V_dot = m_dot / ρ
    # 计算体积流量：V_dot = m_dot / ρ
    if density <= 0:
        raise ValueError("Density must be a positive value.")

    volume_flow_rate_m3_s = mass_flow_rate_kg_s / density  # m³/s
    volume_flow_rate_L_s = volume_flow_rate_m3_s * 1000    # L/s (since 1 m³ = 1000 L)
    volume_flow_rate_m3_h = volume_flow_rate_m3_s * 3600   # m³/h (since 1 h = 3600 s)

    return volume_flow_rate_m3_s, volume_flow_rate_L_s, volume_flow_rate_m3_h


def calculate_pue(it_power: float, auxiliary_power: float) -> float:
    """
    Calculate Power Usage Effectiveness (PUE) for the liquid cooling subsystem.
    计算液冷子系统的电能使用效率 (PUE)。

    Args:
        it_power: IT equipment power in kW (IT 设备功率，单位 kW)
        auxiliary_power: Auxiliary power (pumps, fans) in kW (辅助功率，水泵、风机，单位 kW)

    Returns:
        PUE value (dimensionless)
        PUE 值（无量纲）
    """
    if it_power <= 0:
        raise ValueError("IT power must be positive.")
    if auxiliary_power < 0:
        raise ValueError("Auxiliary power cannot be negative.")

    total_facility_power = it_power + auxiliary_power  # kW
    pue = total_facility_power / it_power
    return pue


def main() -> None:
    """Main function to parse arguments and display results."""
    parser = argparse.ArgumentParser(
        description="Calculate coolant flow rate and PUE for liquid cooling data centers.\n"
                    "计算液冷数据中心的冷却液流量和 PUE。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--it_power",
        type=float,
        required=True,
        help="IT equipment total power in kW (例如: 100 for 100 kW)\n"
             "IT 设备总功率，单位 kW"
    )
    parser.add_argument(
        "--specific_heat",
        type=float,
        required=True,
        help="Coolant specific heat capacity in kJ/(kg·K) (例如: 4.18 for water, 2.4 for EG/WATER)\n"
             "冷却液比热容，单位 kJ/(kg·K)"
    )
    parser.add_argument(
        "--density",
        type=float,
        required=True,
        help="Coolant density in kg/m³ (例如: 1000 for water, 1100 for EG/WATER mix)\n"
             "冷却液密度，单位 kg/m³"
    )
    parser.add_argument(
        "--delta_t",
        type=float,
        required=True,
        help="Temperature difference between supply and return in K or °C (例如: 5 for 5°C)\n"
             "供回水温差，单位 K 或 °C"
    )
    parser.add_argument(
        "--aux_power",
        type=float,
        default=0.0,
        help="Auxiliary power (pumps, fans) in kW (默认: 0)\n"
             "辅助功率（水泵、风机），单位 kW"
    )

    args = parser.parse_args()

    try:
        # Calculate flow rate
        flow_m3_s, flow_L_s, flow_m3_h = calculate_flow_rate(
            args.it_power,
            args.specific_heat,
            args.density,
            args.delta_t
        )

        # Calculate PUE
        pue_value = calculate_pue(args.it_power, args.aux_power)

        # Heat load that the coolant must remove (equal to IT power in kW)
        heat_load_kw = args.it_power  # kW

        # Cyberpunk style terminal output
        print(f"{colors.BACKGROUND}{colors.BOLD}{colors.CYAN}")
        print("╔═══════════════════════════════════════════════════════════════════════════╗")
        print("║                     🌡️  LIQUID COOLING CDU & PUE CALCULATOR 🌡️                     ║")
        print("║                     液冷数据中心 CDU 和 PUE 计算工具                     ║")
        print("╚════════════════════════════════════════════════════════════════════════════╝")
        print(f"{colors.END}")

        print(f"{colors.BOLD}{colors.YELLOW}📊 INPUT PARAMETERS / 输入参数:{colors.END}")
        print(f"  • IT Power: {args.it_power:>8.2f} kW")
        print(f"  • Coolant Specific Heat: {args.specific_heat:>6.2f} kJ/(kg·K)")
        print(f"  • Coolant Density: {args.density:>8.0f} kg/m³")
        print(f"  • ΔT (Supply-Return): {args.delta_t:>8.2f} K")
        print(f"  • Auxiliary Power (Pumps/Fans): {args.aux_power:>6.2f} kW")
        print()

        print(f"{colors.BOLD}{colors.GREEN}🧮 CALCULATION RESULTS / 计算结果:{colors.END}")
        print(f"  • Heat Load to be Removed: {heat_load_kw:>8.2f} kW")
        print(f"  • Coolant Flow Rate:")
        print(f"      - {flow_m3_s:>10.6f} m³/s")
        print(f"      - {flow_L_s:>10.3f} L/s")
        print(f"      - {flow_m3_h:>10.3f} m³/h")
        print(f"  • Estimated PUE (Cooling Subsystem): {pue_value:>10.3f}")
        print()

        # Add interpretation
        print(f"{colors.BOLD}{colors.BLUE}📝 ENGINEERING NOTES / 工程注释:{colors.END}")
        print(f"  • The coolant flow rate is calculated based on the formula:")
        print(f"      V_dot = P / (ρ * c * ΔT)")
        print(f"  • PUE estimation assumes that the only additional facility power")
        print(f"    beyond IT load is from pumps and fans (auxiliary power).")
        print(f"    Actual PUE may include other losses (lighting, controls, etc.).")
        print(f"  • For cold plate liquid cooling, typical PUE ranges from 1.10 to 1.30")
        print(f"    depending on auxiliary power and climate (free cooling potential).")
        print(f"  • Ensure coolant properties are for the actual operating temperature.")
        print()

        # Cyberpunk footer
        print(f"{colors.BACKGROUND}{colors.BOLD}{colors.MAGENTA}")
        print("╔════════════════════════════════════════════════════════════════════════════╗")
        print("║  💻  Stay cyberpunk, stay efficient. 计算由赛博朋克工程师提供  💻  ║")
        print("╚════════════════════════════════════════════════════════════════════════════╝")
        print(f"{colors.END}")

    except ValueError as e:
        print(f"{colors.BOLD}{colors.RED}❌ ERROR / 错误: {e}{colors.END}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"{colors.BOLD}{colors.RED}❌ UNEXPECTED ERROR / 意外错误: {e}{colors.END}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()