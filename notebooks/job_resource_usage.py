#!/usr/bin/env python3
"""
Extract performance statistics from LSF job output logs.
Usage: python extract_job_stats.py <logfile>
"""

import sys
import re
from pathlib import Path


def parse_lsf_output(log_file):
    """
    Parse LSF job output file and extract resource usage statistics.
    
    Args:
        log_file (str): Path to the LSF output log file
    
    Returns:
        dict: Dictionary containing job statistics
    """
    stats = {}
    
    try:
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Extract job ID from filename or content
        job_id_match = re.search(r'Job ID:\s*(\d+)', content)
        if job_id_match:
            stats['job_id'] = job_id_match.group(1)
        else:
            # Try to get from filename
            filename_match = re.search(r'\.(\d+)\.log', log_file)
            if filename_match:
                stats['job_id'] = filename_match.group(1)
        
        # Extract job name
        job_name_match = re.search(r'#BSUB -J\s+(\S+)', content)
        if job_name_match:
            stats['job_name'] = job_name_match.group(1)
        
        # Extract requested resources
        cpu_match = re.search(r'#BSUB -n\s+(\d+)', content)
        if cpu_match:
            stats['requested_cpus'] = int(cpu_match.group(1))
        
        mem_match = re.search(r'#BSUB -R\s+"rusage\[mem=([0-9.]+)([GM]B)\]"', content)
        if mem_match:
            mem_value = float(mem_match.group(1))
            mem_unit = mem_match.group(2)
            stats['requested_memory'] = f"{mem_value} {mem_unit}"
        
        time_match = re.search(r'#BSUB -W\s+(\d+):(\d+)', content)
        if time_match:
            hours = int(time_match.group(1))
            minutes = int(time_match.group(2))
            stats['requested_time'] = f"{hours}:{minutes:02d}"
        
        # Extract actual resource usage
        cpu_time_match = re.search(r'CPU time\s*:\s*([0-9.]+)\s*sec', content)
        if cpu_time_match:
            stats['cpu_time_sec'] = float(cpu_time_match.group(1))
            stats['cpu_time_min'] = round(float(cpu_time_match.group(1)) / 60, 2)
        
        max_mem_match = re.search(r'Max Memory\s*:\s*([0-9.]+)\s*(GB|MB)', content)
        if max_mem_match:
            stats['max_memory_used'] = f"{max_mem_match.group(1)} {max_mem_match.group(2)}"
        
        avg_mem_match = re.search(r'Average Memory\s*:\s*([0-9.]+)\s*(GB|MB)', content)
        if avg_mem_match:
            stats['avg_memory_used'] = f"{avg_mem_match.group(1)} {avg_mem_match.group(2)}"
        
        delta_mem_match = re.search(r'Delta Memory\s*:\s*([0-9.]+)\s*(GB|MB)', content)
        if delta_mem_match:
            stats['unused_memory'] = f"{delta_mem_match.group(1)} {delta_mem_match.group(2)}"
        
        run_time_match = re.search(r'Run time\s*:\s*([0-9.]+)\s*sec', content)
        if run_time_match:
            stats['run_time_sec'] = float(run_time_match.group(1))
            stats['run_time_min'] = round(float(run_time_match.group(1)) / 60, 2)
        
        turnaround_match = re.search(r'Turnaround time\s*:\s*([0-9.]+)\s*sec', content)
        if turnaround_match:
            stats['turnaround_time_sec'] = float(turnaround_match.group(1))
        
        max_threads_match = re.search(r'Max Threads\s*:\s*(\d+)', content)
        if max_threads_match:
            stats['max_threads'] = int(max_threads_match.group(1))
        
        # Check job status
        if 'Successfully completed' in content:
            stats['status'] = 'COMPLETED'
        elif 'Exited with exit code' in content:
            stats['status'] = 'FAILED'
        else:
            stats['status'] = 'UNKNOWN'
        
        return stats
    
    except FileNotFoundError:
        print(f"Error: File '{log_file}' not found.")
        return None
    except Exception as e:
        print(f"Error parsing file: {e}")
        return None


def calculate_efficiency(stats):
    """Calculate resource efficiency metrics."""
    efficiency = {}
    
    # CPU efficiency
    if 'cpu_time_sec' in stats and 'run_time_sec' in stats and 'requested_cpus' in stats:
        theoretical_max = stats['run_time_sec'] * stats['requested_cpus']
        cpu_efficiency = (stats['cpu_time_sec'] / theoretical_max) * 100
        efficiency['cpu_efficiency'] = round(cpu_efficiency, 1)
    
    # Memory efficiency
    if 'max_memory_used' in stats and 'requested_memory' in stats:
        # Parse values
        max_used = float(stats['max_memory_used'].split()[0])
        requested = float(stats['requested_memory'].split()[0])
        
        # Convert to same units if needed
        max_unit = stats['max_memory_used'].split()[1]
        req_unit = stats['requested_memory'].split()[1]
        
        if max_unit == 'MB' and req_unit == 'GB':
            max_used = max_used / 1024
        elif max_unit == 'GB' and req_unit == 'MB':
            requested = requested / 1024
        
        mem_efficiency = (max_used / requested) * 100
        efficiency['memory_efficiency'] = round(mem_efficiency, 1)
    
    return efficiency


def print_report(stats, efficiency):
    """Print a formatted report of job statistics."""
    print("\n" + "="*60)
    print("LSF JOB PERFORMANCE REPORT")
    print("="*60)
    
    if 'job_name' in stats:
        print(f"Job Name: {stats['job_name']}")
    if 'job_id' in stats:
        print(f"Job ID: {stats['job_id']}")
    if 'status' in stats:
        print(f"Status: {stats['status']}")
    
    print("\n" + "-"*60)
    print("REQUESTED RESOURCES")
    print("-"*60)
    
    if 'requested_cpus' in stats:
        print(f"CPUs: {stats['requested_cpus']}")
    if 'requested_memory' in stats:
        print(f"Memory: {stats['requested_memory']}")
    if 'requested_time' in stats:
        print(f"Time: {stats['requested_time']}")
    
    print("\n" + "-"*60)
    print("ACTUAL USAGE")
    print("-"*60)
    
    if 'run_time_min' in stats:
        print(f"Run Time: {stats['run_time_min']} min ({stats['run_time_sec']} sec)")
    if 'cpu_time_min' in stats:
        print(f"CPU Time: {stats['cpu_time_min']} min ({stats['cpu_time_sec']} sec)")
    if 'max_memory_used' in stats:
        print(f"Max Memory: {stats['max_memory_used']}")
    if 'avg_memory_used' in stats:
        print(f"Avg Memory: {stats['avg_memory_used']}")
    if 'unused_memory' in stats:
        print(f"Unused Memory: {stats['unused_memory']}")
    if 'max_threads' in stats:
        print(f"Max Threads: {stats['max_threads']}")
    
    if efficiency:
        print("\n" + "-"*60)
        print("EFFICIENCY METRICS")
        print("-"*60)
        
        if 'cpu_efficiency' in efficiency:
            cpu_eff = efficiency['cpu_efficiency']
            print(f"CPU Efficiency: {cpu_eff}%", end="")
            if cpu_eff < 50:
                print(" ⚠️  LOW - Consider reducing cores")
            elif cpu_eff > 90:
                print(" ✓ EXCELLENT")
            else:
                print(" ✓ GOOD")
        
        if 'memory_efficiency' in efficiency:
            mem_eff = efficiency['memory_efficiency']
            print(f"Memory Efficiency: {mem_eff}%", end="")
            if mem_eff < 50:
                print(" ⚠️  LOW - Consider reducing memory request")
            elif mem_eff > 90:
                print(" ⚠️  HIGH - Consider increasing memory request")
            else:
                print(" ✓ GOOD")
    
    print("\n" + "="*60)
    
    # Recommendations
    print("\nRECOMMENDATIONS:")
    print("-"*60)
    
    recommendations = []
    
    if efficiency.get('cpu_efficiency', 100) < 50:
        recommendations.append("• Reduce number of cores - CPU utilization is low")
    
    if efficiency.get('memory_efficiency', 100) < 40:
        recommendations.append("• Reduce memory request - significant unused memory")
    
    if efficiency.get('memory_efficiency', 0) > 95:
        recommendations.append("• Increase memory request - running close to limit")
    
    if 'run_time_min' in stats and 'requested_time' in stats:
        requested_min = int(stats['requested_time'].split(':')[0]) * 60 + int(stats['requested_time'].split(':')[1])
        if stats['run_time_min'] < requested_min * 0.3:
            recommendations.append("• Reduce time request - job finished much earlier than expected")
    
    if recommendations:
        for rec in recommendations:
            print(rec)
    else:
        print("• Resource requests appear well-optimized! ✓")
    
    print()


def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_job_stats.py <logfile>")
        print("Example: python extract_job_stats.py output.415350.log")
        sys.exit(1)
    
    log_file = sys.argv[1]
    
    stats = parse_lsf_output(log_file)
    
    if stats is None:
        sys.exit(1)
    
    efficiency = calculate_efficiency(stats)
    
    print_report(stats, efficiency)


if __name__ == "__main__":
    main()