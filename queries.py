"""Plain-English query catalog for IBM Storage Virtualize `ls*` commands.

Each catalog entry maps a friendly, searchable query to a real read-only CLI
command. `columns` (optional) lists the fields to surface first in the results
table; `formatters` maps a column name to a formatter hint used by the UI
(``capacity`` humanizes byte/GB/TB values, ``status`` renders a colored chip).

ALL_LS_COMMANDS is the authoritative list of every ``ls*`` command extracted
from the IBM Storage Virtualize Command-Line Interface guide; it powers the
autocomplete in the Advanced (free-form) box.
"""

# --- Curated plain-English queries -----------------------------------------
# Fields:
#   id          stable identifier
#   label       what the user sees / searches
#   category    grouping in the UI
#   keywords    extra search terms (synonyms an admin might type)
#   command     the CLI command actually run (always read-only, starts with ls)
#   description one-line explanation
#   columns     preferred columns to show first (others still available)
#   formatters  {column: "capacity"|"status"}

CATALOG = [
    # ---- Volumes ----
    {
        "id": "all_volumes",
        "label": "Show all volumes",
        "category": "Volumes",
        "keywords": ["volumes", "vdisk", "vdisks", "luns", "disks", "list volumes"],
        "command": "lsvdisk",
        "description": "Every volume (vdisk) on the system with pool, status and capacity.",
        "columns": ["id", "name", "status", "mdisk_grp_name", "capacity", "type"],
        "formatters": {"capacity": "capacity", "status": "status"},
    },
    {
        "id": "volume_capacity",
        "label": "Capacity of all volumes",
        "category": "Volumes",
        "keywords": ["capacity", "size", "space", "how big", "volume size", "gb", "tb"],
        "command": "lsvdisk",
        "description": "Volume names and their provisioned capacity (with a total).",
        "columns": ["name", "capacity", "mdisk_grp_name", "status"],
        "formatters": {"capacity": "capacity", "status": "status"},
    },
    {
        "id": "volume_host_map",
        "label": "Volume-to-host mappings",
        "category": "Volumes",
        "keywords": ["mapping", "mapped", "host map", "which host", "masking", "presented"],
        "command": "lshostvdiskmap",
        "description": "Which volumes are mapped to which hosts.",
        "columns": ["id", "name", "SCSI_id", "vdisk_id", "vdisk_name", "vdisk_UID"],
        "formatters": {},
    },
    {
        "id": "volume_copies",
        "label": "Volume copies (mirroring)",
        "category": "Volumes",
        "keywords": ["copy", "mirror", "vdiskcopy", "sync"],
        "command": "lsvdiskcopy",
        "description": "Volume copies used for volume mirroring.",
        "columns": ["vdisk_id", "vdisk_name", "copy_id", "status", "sync", "mdisk_grp_name", "capacity"],
        "formatters": {"capacity": "capacity", "status": "status"},
    },
    # ---- Pools / capacity ----
    {
        "id": "pools",
        "label": "List storage pools",
        "category": "Pools & Capacity",
        "keywords": ["pool", "pools", "mdiskgrp", "storage pool", "disk group"],
        "command": "lsmdiskgrp",
        "description": "Storage pools (managed disk groups) with capacity and status.",
        "columns": ["id", "name", "status", "capacity", "free_capacity", "used_capacity", "virtual_capacity"],
        "formatters": {"capacity": "capacity", "free_capacity": "capacity",
                       "used_capacity": "capacity", "virtual_capacity": "capacity",
                       "real_capacity": "capacity", "status": "status"},
    },
    {
        "id": "pool_free",
        "label": "Pool free / used capacity",
        "category": "Pools & Capacity",
        "keywords": ["free space", "used", "utilization", "full", "remaining", "available"],
        "command": "lsmdiskgrp",
        "description": "Free and used capacity per pool to spot pools filling up.",
        "columns": ["name", "capacity", "free_capacity", "used_capacity", "status"],
        "formatters": {"capacity": "capacity", "free_capacity": "capacity",
                       "used_capacity": "capacity", "status": "status"},
    },
    {
        "id": "system_capacity",
        "label": "Overall system capacity",
        "category": "Pools & Capacity",
        "keywords": ["total capacity", "system capacity", "usable", "data reduction", "savings"],
        "command": "lssystemcapacity",
        "description": "System-wide physical, usable and used capacity.",
        "columns": [],
        "formatters": {},
    },
    {
        "id": "free_extents",
        "label": "Free extents per MDisk",
        "category": "Pools & Capacity",
        "keywords": ["extents", "free extents"],
        "command": "lsfreeextents",
        "description": "Free extents available on managed disks.",
        "columns": [],
        "formatters": {},
    },
    # ---- Hosts ----
    {
        "id": "hosts",
        "label": "List hosts",
        "category": "Hosts",
        "keywords": ["host", "hosts", "servers", "initiators", "clients"],
        "command": "lshost",
        "description": "Defined hosts and their connection status.",
        "columns": ["id", "name", "status", "host_cluster_name", "port_count", "type"],
        "formatters": {"status": "status"},
    },
    {
        "id": "host_clusters",
        "label": "List host clusters",
        "category": "Hosts",
        "keywords": ["host cluster", "cluster", "grouped hosts"],
        "command": "lshostcluster",
        "description": "Host clusters and how many hosts/mappings each has.",
        "columns": ["id", "name", "status", "host_count", "mapping_count"],
        "formatters": {"status": "status"},
    },
    {
        "id": "host_map",
        "label": "Host-to-volume mappings",
        "category": "Hosts",
        "keywords": ["what does host see", "host volumes", "vdiskhostmap"],
        "command": "lsvdiskhostmap",
        "description": "Which hosts each volume is mapped to.",
        "columns": [],
        "formatters": {},
    },
    # ---- Physical storage ----
    {
        "id": "mdisks",
        "label": "List managed disks (MDisks)",
        "category": "Physical Storage",
        "keywords": ["mdisk", "mdisks", "managed disk", "backend"],
        "command": "lsmdisk",
        "description": "Managed disks and the pool each belongs to.",
        "columns": ["id", "name", "status", "mode", "mdisk_grp_name", "capacity", "tier"],
        "formatters": {"capacity": "capacity", "status": "status"},
    },
    {
        "id": "drives",
        "label": "List physical drives",
        "category": "Physical Storage",
        "keywords": ["drive", "drives", "disk", "ssd", "hdd", "flash", "nvme"],
        "command": "lsdrive",
        "description": "Physical drives with status, use, capacity and tech type.",
        "columns": ["id", "status", "use", "capacity", "tech_type", "mdisk_name", "enclosure_id", "slot_id"],
        "formatters": {"capacity": "capacity", "status": "status"},
    },
    {
        "id": "arrays",
        "label": "List arrays (RAID)",
        "category": "Physical Storage",
        "keywords": ["array", "arrays", "raid", "distributed array", "draid"],
        "command": "lsarray",
        "description": "RAID/DRAID arrays and their status.",
        "columns": ["mdisk_id", "mdisk_name", "status", "raid_level", "redundancy", "capacity", "tier"],
        "formatters": {"capacity": "capacity", "status": "status"},
    },
    {
        "id": "enclosures",
        "label": "List enclosures",
        "category": "Physical Storage",
        "keywords": ["enclosure", "enclosures", "shelf", "control", "expansion"],
        "command": "lsenclosure",
        "description": "Control and expansion enclosures with status.",
        "columns": ["id", "status", "type", "product_MTM", "serial_number", "total_canisters", "online_canisters"],
        "formatters": {"status": "status"},
    },
    {
        "id": "controllers",
        "label": "List external storage controllers",
        "category": "Physical Storage",
        "keywords": ["controller", "external storage", "virtualized backend"],
        "command": "lscontroller",
        "description": "External storage controllers being virtualized.",
        "columns": ["id", "controller_name", "ctrl_s/n", "vendor_id", "product_id_low"],
        "formatters": {},
    },
    # ---- System / hardware ----
    {
        "id": "system",
        "label": "System summary / health",
        "category": "System & Hardware",
        "keywords": ["system", "cluster", "overview", "health", "summary", "info", "firmware", "version", "code level"],
        "command": "lssystem",
        "description": "System-wide properties: name, code level, topology, capacity.",
        "columns": [],
        "formatters": {},
    },
    {
        "id": "nodes",
        "label": "List nodes / canisters",
        "category": "System & Hardware",
        "keywords": ["node", "nodes", "canister", "canisters", "controllers"],
        "command": "lsnodecanister",
        "description": "Node canisters, their status and config role.",
        "columns": ["id", "name", "status", "config_node", "panel_name", "enclosure_id", "IO_group_name"],
        "formatters": {"status": "status"},
    },
    {
        "id": "iogroups",
        "label": "List I/O groups",
        "category": "System & Hardware",
        "keywords": ["io group", "iogrp", "io groups", "caching"],
        "command": "lsiogrp",
        "description": "I/O groups and how many nodes/volumes each has.",
        "columns": ["id", "name", "node_count", "vdisk_count", "host_count"],
        "formatters": {},
    },
    {
        "id": "hardware",
        "label": "Node hardware inventory",
        "category": "System & Hardware",
        "keywords": ["hardware", "cpu", "memory", "vpd", "model"],
        "command": "lsnodecanisterhw",
        "description": "Per-node hardware details (CPU, memory, ports).",
        "columns": [],
        "formatters": {},
    },
    {
        "id": "system_stats",
        "label": "Live system performance stats",
        "category": "System & Hardware",
        "keywords": ["performance", "iops", "latency", "throughput", "stats", "cpu busy"],
        "command": "lssystemstats",
        "description": "Most recent performance statistics for the system.",
        "columns": [],
        "formatters": {},
    },
    # ---- Ports & connectivity ----
    {
        "id": "fc_ports",
        "label": "List Fibre Channel ports",
        "category": "Ports & Connectivity",
        "keywords": ["fc port", "fibre channel", "wwpn", "san ports"],
        "command": "lsportfc",
        "description": "Fibre Channel ports, WWPN and link status.",
        "columns": ["id", "fc_io_port_id", "port_id", "type", "port_speed", "status", "attachment"],
        "formatters": {"status": "status"},
    },
    {
        "id": "ip_ports",
        "label": "List IP / iSCSI ports",
        "category": "Ports & Connectivity",
        "keywords": ["ip port", "ethernet", "iscsi", "network port"],
        "command": "lsportip",
        "description": "Ethernet/iSCSI port configuration and link state.",
        "columns": [],
        "formatters": {"status": "status", "link_state": "status"},
    },
    {
        "id": "fabric",
        "label": "SAN fabric connectivity",
        "category": "Ports & Connectivity",
        "keywords": ["fabric", "zoning", "logins", "connectivity", "wwn"],
        "command": "lsfabric",
        "description": "Fibre Channel logins between nodes, hosts and controllers.",
        "columns": [],
        "formatters": {},
    },
    # ---- Copy services / replication ----
    {
        "id": "flashcopy",
        "label": "FlashCopy mappings",
        "category": "Copy Services",
        "keywords": ["flashcopy", "fcmap", "snapshot map", "clone", "point in time"],
        "command": "lsfcmap",
        "description": "FlashCopy mappings and their progress/status.",
        "columns": ["id", "name", "source_vdisk_name", "target_vdisk_name", "status", "progress"],
        "formatters": {"status": "status"},
    },
    {
        "id": "rcrelationships",
        "label": "Remote copy relationships",
        "category": "Copy Services",
        "keywords": ["remote copy", "replication", "metro mirror", "global mirror", "rcrelationship", "dr"],
        "command": "lsrcrelationship",
        "description": "Metro/Global Mirror replication relationships.",
        "columns": ["id", "name", "master_vdisk_name", "aux_vdisk_name", "state", "progress", "copy_type"],
        "formatters": {"state": "status"},
    },
    {
        "id": "partnerships",
        "label": "Replication partnerships",
        "category": "Copy Services",
        "keywords": ["partnership", "partner", "remote system", "replication link"],
        "command": "lspartnership",
        "description": "Partnerships with remote systems for replication.",
        "columns": ["id", "name", "location", "partnership", "type"],
        "formatters": {"partnership": "status"},
    },
    {
        "id": "volume_groups",
        "label": "List volume groups",
        "category": "Copy Services",
        "keywords": ["volume group", "volumegroup", "consistency", "application group"],
        "command": "lsvolumegroup",
        "description": "Volume groups used for snapshots and replication policies.",
        "columns": ["id", "name", "volume_count", "snapshot_count"],
        "formatters": {},
    },
    {
        "id": "snapshots",
        "label": "List snapshots",
        "category": "Copy Services",
        "keywords": ["snapshot", "snapshots", "safeguarded", "backup point"],
        "command": "lsvolumegroupsnapshot",
        "description": "Volume group snapshots (including Safeguarded Copies).",
        "columns": [],
        "formatters": {},
    },
    # ---- Events / admin ----
    {
        "id": "eventlog",
        "label": "Event log (alerts / errors)",
        "category": "Events & Admin",
        "keywords": ["event", "events", "error", "errors", "alerts", "log", "problems", "faults"],
        "command": "lseventlog",
        "description": "Recent events, alerts and unfixed errors.",
        "columns": ["sequence_number", "last_timestamp", "object_type", "object_name", "status", "error_code", "description"],
        "formatters": {"status": "status"},
    },
    {
        "id": "users",
        "label": "List users",
        "category": "Events & Admin",
        "keywords": ["user", "users", "accounts", "logins", "admin"],
        "command": "lsuser",
        "description": "Configured user accounts and their roles.",
        "columns": ["id", "name", "usergrp_name", "remote"],
        "formatters": {},
    },
    {
        "id": "usergroups",
        "label": "List user groups / roles",
        "category": "Events & Admin",
        "keywords": ["user group", "role", "roles", "rbac", "usergrp"],
        "command": "lsusergrp",
        "description": "User groups and their role/permissions.",
        "columns": ["id", "name", "role", "remote"],
        "formatters": {},
    },
    {
        "id": "licenses",
        "label": "List licenses",
        "category": "Events & Admin",
        "keywords": ["license", "licenses", "licensing", "entitlement", "feature"],
        "command": "lslicense",
        "description": "Licensed features and limits.",
        "columns": [],
        "formatters": {},
    },
    {
        "id": "quorum",
        "label": "List quorum devices",
        "category": "Events & Admin",
        "keywords": ["quorum", "tie breaker", "witness"],
        "command": "lsquorum",
        "description": "Quorum devices/IP quorum apps and their status.",
        "columns": ["quorum_index", "status", "id", "name", "controller_id", "active", "object_type"],
        "formatters": {"status": "status"},
    },
    {
        "id": "throttles",
        "label": "List throttles (QoS)",
        "category": "Events & Admin",
        "keywords": ["throttle", "qos", "rate limit", "iops limit", "bandwidth limit"],
        "command": "lsthrottle",
        "description": "Configured throttles (IOPS/bandwidth limits).",
        "columns": ["throttle_id", "throttle_name", "object_id", "object_name", "throttle_type", "IOPs_limit", "bandwidth_limit_MB"],
        "formatters": {},
    },
]

# --- Full authoritative ls* command list (for the Advanced box autocomplete) -
# Extracted from the IBM Storage Virtualize Command-Line Interface guide.
ALL_LS_COMMANDS = [
    "lsarray", "lsarraymember", "lsarrayrecommendation", "lsauth", "lsautoupdate",
    "lsavailablepatch", "lsbootdrive", "lscloudaccount", "lscloudaccountusage",
    "lscloudcallhome", "lscontroller", "lscontrollerports", "lscopystatus",
    "lscurrentuser", "lsdependentvdisks", "lsdiscoverystatus", "lsdnsserver",
    "lsdrive", "lsdriveclass", "lsemailserver", "lsemailuser", "lsenclosure",
    "lsenclosurebattery", "lsenclosurecanister", "lsenclosurepsu", "lsenclosureslot",
    "lsenclosurestats", "lsencryption", "lseventlog", "lsfabric", "lsfcconsistgrp",
    "lsfcmap", "lsfcmapprogress", "lsfcportsetmember", "lsfeature", "lsfreeextents",
    "lshardware", "lshost", "lshostcluster", "lshostclustermember",
    "lshostclustervolumemap", "lshostiogrp", "lshostvdiskmap", "lsiogrp",
    "lsiogrphost", "lsip", "lsiscsiauth", "lskeyserver", "lsldap", "lsldapserver",
    "lslicense", "lslocaldisk", "lsmdisk", "lsmdiskcandidate", "lsmdiskextent",
    "lsmdiskgrp", "lsmdiskmember", "lsmigrate", "lsnode", "lsnodebattery",
    "lsnodebootdrive", "lsnodecanister", "lsnodecanisterhw", "lsnodecanisterstats",
    "lsnodecanistervpd", "lsnodehw", "lsnodeip", "lsnodestats", "lsnodevpd",
    "lsownershipgroup", "lspartition", "lspartnership", "lspatch",
    "lsportethernet", "lsportfc", "lsportip", "lsportsas", "lsportset",
    "lsportstats", "lsprovisioningpolicy", "lsproxy", "lsquorum",
    "lsreplicationpolicy", "lsroute", "lssafeguardedpolicy", "lssafeguardedschedule",
    "lssasfabric", "lssecurity", "lsservicenodes", "lsservicestatus",
    "lssevdiskcopy", "lssite", "lssnapshotpolicy", "lssnapshotschedule",
    "lssnmpserver", "lssra", "lssyslogserver", "lssystem", "lssystemcapacity",
    "lssystemcert", "lssystemethernet", "lssystemip", "lssystemlimits",
    "lssystemstats", "lssystemsupportcenter", "lstargetportfc", "lsthrottle",
    "lstimezones", "lstruststore", "lsupdate", "lsuser", "lsusergrp", "lsvcenter",
    "lsvdisk", "lsvdiskaccess", "lsvdiskanalysis", "lsvdiskcopy",
    "lsvdiskhostmap", "lsvdiskmember", "lsvolumegroup", "lsvolumegrouppopulation",
    "lsvolumegroupreplication", "lsvolumegroupsnapshot", "lsvolumepopulation",
    "lsvolumesnapshot",
]


def public_catalog():
    """Catalog trimmed to the fields the front end needs (no internals hidden)."""
    return [
        {
            "id": e["id"],
            "label": e["label"],
            "category": e["category"],
            "keywords": e.get("keywords", []),
            "command": e["command"],
            "description": e["description"],
            "columns": e.get("columns", []),
            "formatters": e.get("formatters", {}),
        }
        for e in CATALOG
    ]


def find_entry(entry_id):
    for e in CATALOG:
        if e["id"] == entry_id:
            return e
    return None
