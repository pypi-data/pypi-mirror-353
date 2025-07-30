from typing import Annotated, Optional
from pydantic import Field
from multicluster_mcp_server.tools.connect import setup_cluster_access, get_kubeconfig_file
from multicluster_mcp_server.tools.kubectl import validate_kubeconfig_file
from multicluster_mcp_server.utils.prom_connect import prom_connect
from multicluster_mcp_server.core.mcp_instance import mcp
from prometheus_api_client import PrometheusConnect, MetricSnapshotDataFrame, MetricRangeDataFrame

@mcp.tool(description="Query Prometheus metrics from a specific cluster and format the results for Recharts visualization.")
def prometheus(
    ql: Annotated[str, Field(description="The PromQL query string to run against the Prometheus server.")],
    data_type: Annotated[str, Field(description="Type of query: 'snapshot' for instant or 'range' for time-series.")] = "snapshot",
    group_by: Annotated[str, Field(description="Label to group results by, such as 'pod' or 'namespace'.")] = "pod",
    unit: Annotated[str, Field(description="The desired output unit: 'auto', 'bytes', 'MiB', 'GiB', 'cores', or 'millicores'.")] = "auto",
    cluster: Annotated[Optional[str], Field(description="The target cluster name. Defaults to the hub cluster.")] = None,
) -> Annotated[dict, Field(description="Formatted result including Recharts-compatible data or error message.")]:
    try:
        def infer_unit(unit: str, query: str) -> str:
            if unit != "auto":
                return unit
            q = query.lower()
            if "memory" in q or "bytes" in q:
                return "GiB"
            elif "cpu" in q:
                return "cores"
            return "raw"

        def transform_value(value: float, unit: str) -> float:
            value = float(value)
            if unit == "MiB":
                return value / (1024 ** 2)
            elif unit == "GiB":
                return value / (1024 ** 3)
            elif unit == "millicores":
                return value * 1000
            return value

        kubeconfig_file = None
        if cluster and cluster != "default":
            kubeconfig_file = get_kubeconfig_file(cluster)
            if not validate_kubeconfig_file(kubeconfig_file):
                kubeconfig_file = setup_cluster_access(cluster)
                if not kubeconfig_file:
                    raise FileNotFoundError(f"KUBECONFIG for cluster '{cluster}' does not exist.")

        pc = prom_connect(kubeconfig=kubeconfig_file)
        result = pc.custom_query(query=ql)

        effective_unit = infer_unit(unit, ql)
        recharts_data = []

        if data_type == "snapshot":
            df = MetricSnapshotDataFrame(result)
            recharts_data = [
                {
                    "name": row.get(group_by, "unknown"),
                    "value": transform_value(row["value"], effective_unit)
                }
                for _, row in df.iterrows()
            ]
        elif data_type == "range":
            df = MetricRangeDataFrame(result)
            df["timestamp"] = df["timestamp"].astype(str)
            for ts, group in df.groupby("timestamp"):
                entry = {"name": ts}
                for _, row in group.iterrows():
                    key = row.get(group_by, "unknown")
                    entry[key] = transform_value(row["value"], effective_unit)
                recharts_data.append(entry)
        else:
            raise ValueError("Invalid data_type. Must be 'snapshot' or 'range'.")

        return {
            "data": recharts_data,
            "type": data_type,
            "unit": effective_unit
        }

    except Exception as e:
        return {"error": str(e)}


      

# Example usage
if __name__ == "__main__":
    sq = '''
          sum by(namespace) (
            container_memory_usage_bytes{
              namespace=~"multicluster-engine|open-cluster-management(-.*)?",
              container!="",
              pod!=""
            }
          )
          '''
    result = prometheus(sq, data_type="snapshot", group_by="namespace", unit="MiB")
    print (result)