def parse_thermal_pressure(powermetrics_parse):
    return powermetrics_parse["thermal_pressure"]


def parse_bandwidth_metrics(powermetrics_parse):
    bandwidth_metrics = powermetrics_parse["bandwidth_counters"]
    bandwidth_metrics_dict = {}
    data_fields = ["PCPU0 DCS RD", "PCPU0 DCS WR",
                   "PCPU1 DCS RD", "PCPU1 DCS WR",
                   "PCPU2 DCS RD", "PCPU2 DCS WR",
                   "PCPU3 DCS RD", "PCPU3 DCS WR",
                   "PCPU DCS RD", "PCPU DCS WR",
                   "ECPU0 DCS RD", "ECPU0 DCS WR",
                   "ECPU1 DCS RD", "ECPU1 DCS WR",
                   "ECPU DCS RD", "ECPU DCS WR",
                   "GFX DCS RD", "GFX DCS WR",
                   "ISP DCS RD", "ISP DCS WR",
                   "STRM CODEC DCS RD", "STRM CODEC DCS WR",
                   "PRORES DCS RD", "PRORES DCS WR",
                   "VDEC DCS RD", "VDEC DCS WR",
                   "VENC0 DCS RD", "VENC0 DCS WR",
                   "VENC1 DCS RD", "VENC1 DCS WR",
                   "VENC2 DCS RD", "VENC2 DCS WR",
                   "VENC3 DCS RD", "VENC3 DCS WR",
                   "VENC DCS RD", "VENC DCS WR",
                   "JPG0 DCS RD", "JPG0 DCS WR",
                   "JPG1 DCS RD", "JPG1 DCS WR",
                   "JPG2 DCS RD", "JPG2 DCS WR",
                   "JPG3 DCS RD", "JPG3 DCS WR",
                   "JPG DCS RD", "JPG DCS WR",
                   "DCS RD", "DCS WR"]
    for h in data_fields:
        bandwidth_metrics_dict[h] = 0
    for l in bandwidth_metrics:
        if l["name"] in data_fields:
            bandwidth_metrics_dict[l["name"]] = l["value"]/(1e9)
    bandwidth_metrics_dict["PCPU DCS RD"] = bandwidth_metrics_dict["PCPU DCS RD"] + \
        bandwidth_metrics_dict["PCPU0 DCS RD"] + \
        bandwidth_metrics_dict["PCPU1 DCS RD"] + \
        bandwidth_metrics_dict["PCPU2 DCS RD"] + \
        bandwidth_metrics_dict["PCPU3 DCS RD"]
    bandwidth_metrics_dict["PCPU DCS WR"] = bandwidth_metrics_dict["PCPU DCS WR"] + \
        bandwidth_metrics_dict["PCPU0 DCS WR"] + \
        bandwidth_metrics_dict["PCPU1 DCS WR"] + \
        bandwidth_metrics_dict["PCPU2 DCS WR"] + \
        bandwidth_metrics_dict["PCPU3 DCS WR"]
    bandwidth_metrics_dict["JPG DCS RD"] = bandwidth_metrics_dict["JPG DCS RD"] + \
        bandwidth_metrics_dict["JPG0 DCS RD"] + \
        bandwidth_metrics_dict["JPG1 DCS RD"] + \
        bandwidth_metrics_dict["JPG2 DCS RD"] + \
        bandwidth_metrics_dict["JPG3 DCS RD"]
    bandwidth_metrics_dict["JPG DCS WR"] = bandwidth_metrics_dict["JPG DCS WR"] + \
        bandwidth_metrics_dict["JPG0 DCS WR"] + \
        bandwidth_metrics_dict["JPG1 DCS WR"] + \
        bandwidth_metrics_dict["JPG2 DCS WR"] + \
        bandwidth_metrics_dict["JPG3 DCS WR"]
    bandwidth_metrics_dict["VENC DCS RD"] = bandwidth_metrics_dict["VENC DCS RD"] + \
        bandwidth_metrics_dict["VENC0 DCS RD"] + \
        bandwidth_metrics_dict["VENC1 DCS RD"] + \
        bandwidth_metrics_dict["VENC2 DCS RD"] + \
        bandwidth_metrics_dict["VENC3 DCS RD"]
    bandwidth_metrics_dict["VENC DCS WR"] = bandwidth_metrics_dict["VENC DCS WR"] + \
        bandwidth_metrics_dict["VENC0 DCS WR"] + \
        bandwidth_metrics_dict["VENC1 DCS WR"] + \
        bandwidth_metrics_dict["VENC2 DCS WR"] + \
        bandwidth_metrics_dict["VENC3 DCS WR"]
    bandwidth_metrics_dict["MEDIA DCS"] = sum([
        bandwidth_metrics_dict["ISP DCS RD"], bandwidth_metrics_dict["ISP DCS WR"],
        bandwidth_metrics_dict["STRM CODEC DCS RD"], bandwidth_metrics_dict["STRM CODEC DCS WR"],
        bandwidth_metrics_dict["PRORES DCS RD"], bandwidth_metrics_dict["PRORES DCS WR"],
        bandwidth_metrics_dict["VDEC DCS RD"], bandwidth_metrics_dict["VDEC DCS WR"],
        bandwidth_metrics_dict["VENC DCS RD"], bandwidth_metrics_dict["VENC DCS WR"],
        bandwidth_metrics_dict["JPG DCS RD"], bandwidth_metrics_dict["JPG DCS WR"],
    ])
    return bandwidth_metrics_dict


def _cluster_type(name):
    """Map a raw powermetrics cluster name to a canonical type.

    Prefix rules (case-insensitive first character):
      'E' → efficiency cluster
      'P' → performance cluster
      'S' → super/spill high-performance cluster (M5+), treated as P for display
    Falls back to 'P' for any unrecognised prefix so new clusters degrade
    gracefully rather than crashing.
    """
    prefix = name[0].upper()
    if prefix == 'E':
        return 'E-Cluster'
    elif prefix in ('P', 'S'):
        return 'P-Cluster'
    else:
        return 'P-Cluster'


def parse_cpu_metrics(powermetrics_parse):
    e_core = []
    p_core = []
    cpu_metrics = powermetrics_parse["processor"]
    cpu_metric_dict = {}
    # cpu_clusters
    cpu_clusters = cpu_metrics["clusters"]
    for cluster in cpu_clusters:
        cluster_name = cluster["name"]
        cluster_type = _cluster_type(cluster_name)
        cpu_metric_dict[cluster_name + "_freq_Mhz"] = int(cluster["freq_hz"] / (1e6))
        cpu_metric_dict[cluster_name + "_active"] = int((1 - cluster["idle_ratio"]) * 100)
        for cpu in cluster["cpus"]:
            core = e_core if cluster_type == 'E-Cluster' else p_core
            core.append(cpu["cpu"])
            cpu_metric_dict[cluster_type + str(cpu["cpu"]) + "_freq_Mhz"] = int(cpu["freq_hz"] / (1e6))
            cpu_metric_dict[cluster_type + str(cpu["cpu"]) + "_active"] = int((1 - cpu["idle_ratio"]) * 100)
    cpu_metric_dict["e_core"] = e_core
    cpu_metric_dict["p_core"] = p_core

    # Dynamically aggregate all E-type cluster metrics into the canonical
    # "E-Cluster" key expected by the rest of the code.  On chips with no
    # efficiency clusters (e.g. M5) the lowest-frequency P cluster is used
    # as the E-CPU stand-in so the display still has something meaningful.
    if "E-Cluster_active" not in cpu_metric_dict:
        e_names = [c["name"] for c in cpu_clusters if _cluster_type(c["name"]) == 'E-Cluster']
        if e_names:
            actives = [cpu_metric_dict[n + "_active"] for n in e_names]
            freqs   = [cpu_metric_dict[n + "_freq_Mhz"] for n in e_names]
            cpu_metric_dict["E-Cluster_active"]   = int(sum(actives) / len(actives))
            cpu_metric_dict["E-Cluster_freq_Mhz"] = max(freqs)
        else:
            # No E clusters (e.g. M5): use the lowest-frequency cluster as proxy
            lowest = min(cpu_clusters, key=lambda c: c["freq_hz"])
            lname  = lowest["name"]
            cpu_metric_dict["E-Cluster_active"]   = cpu_metric_dict[lname + "_active"]
            cpu_metric_dict["E-Cluster_freq_Mhz"] = cpu_metric_dict[lname + "_freq_Mhz"]

    # Dynamically aggregate all P-type (and S-type) cluster metrics into the
    # canonical "P-Cluster" key.  On M5 this covers P0, P1, and S-Cluster;
    # on M1 Ultra it covers P0–P3.
    if "P-Cluster_active" not in cpu_metric_dict:
        p_names = [c["name"] for c in cpu_clusters if _cluster_type(c["name"]) == 'P-Cluster']
        if p_names:
            actives = [cpu_metric_dict[n + "_active"] for n in p_names]
            freqs   = [cpu_metric_dict[n + "_freq_Mhz"] for n in p_names]
            cpu_metric_dict["P-Cluster_active"]   = int(sum(actives) / len(actives))
            cpu_metric_dict["P-Cluster_freq_Mhz"] = max(freqs)
        else:
            cpu_metric_dict["P-Cluster_active"]   = 0
            cpu_metric_dict["P-Cluster_freq_Mhz"] = 0

    # power
    cpu_metric_dict["ane_W"]     = cpu_metrics["ane_energy"] / 1000
    cpu_metric_dict["cpu_W"]     = cpu_metrics["cpu_energy"] / 1000
    cpu_metric_dict["gpu_W"]     = cpu_metrics["gpu_energy"] / 1000
    cpu_metric_dict["package_W"] = cpu_metrics["combined_power"] / 1000
    return cpu_metric_dict


def parse_gpu_metrics(powermetrics_parse):
    gpu_metrics = powermetrics_parse["gpu"]
    gpu_metrics_dict = {
        "freq_MHz": int(gpu_metrics["freq_hz"]),
        "active": int((1 - gpu_metrics["idle_ratio"])*100),
    }
    return gpu_metrics_dict
