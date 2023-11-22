INSERT INTO `hpc_tmd` (
	ts, lat, lon, cond, rain, tc, rh
) VALUES (
	STR_TO_DATE('{{payload.0.time}}', '%Y-%m-%d %H:%i:%s'),
    {{payload.0.lat}},
    {{payload.0.lon}},
    {{payload.0.cond}},
    {{payload.0.rain}},
    {{payload.0.tc}},
    {{payload.0.rh}}
), (
    STR_TO_DATE('{{payload.1.time}}', '%Y-%m-%d %H:%i:%s'),
    {{payload.1.lat}},
    {{payload.1.lon}},
    {{payload.1.cond}},
    {{payload.1.rain}},
    {{payload.1.tc}},
    {{payload.1.rh}}
), (
    STR_TO_DATE('{{payload.2.time}}', '%Y-%m-%d %H:%i:%s'),
    {{payload.2.lat}},
    {{payload.2.lon}},
    {{payload.2.cond}},
    {{payload.2.rain}},
    {{payload.2.tc}},
    {{payload.2.rh}}
);
