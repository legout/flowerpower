# Changelog

## [0.9.13.0] - 2025-04-28

### Changes
- Bump version to 0.9.13.0
- name for hook function can be set by cli creation
- add config option to show/save dag to alllow to draw dag with config
- added a config hook to run-pipeline-on-message
- added option config hook to mqtt cli
- added load_hooks function to cli utils
- added method to add a hook template to the project for a specific pipeline
- added template for mqqt config hook method
- added mosquitto.db for docker
- Corrected output message in pipeline delete for deleting module
- added option to delete hooks in pipeline delete function
- adding pipeline to hooks folder when creating pipeline
- create new hook folder on init
- bugfix: mmh3 was in open-telemetry group chaned to mqtt
- moved mmh3 to mqtt group
- removed unused imports
- added a determinstic client_id creation when connecting to broker as persisten client (clean_session = false)
- added client_id_suffix to allow multiple clients to conect to a broker from same host with different endings
- self._client needs to be set before call to subscribe
- config anpassungeng für tests
- client_id and clean_session from cli overwrites given config
- added custom client_id in MQTTManager
- added clean_session, client_id and qos to cli
- added client_id
- added clean_session and qos in run_pipieline_on_message command



## [0.9.13.0] - 2025-04-28

### Changes
- name for hook function can be set by cli creation
- add config option to show/save dag to alllow to draw dag with config
- added a config hook to run-pipeline-on-message
- added option config hook to mqtt cli
- added load_hooks function to cli utils
- added method to add a hook template to the project for a specific pipeline
- added template for mqqt config hook method
- added mosquitto.db for docker
- Corrected output message in pipeline delete for deleting module
- added option to delete hooks in pipeline delete function
- adding pipeline to hooks folder when creating pipeline
- create new hook folder on init
- bugfix: mmh3 was in open-telemetry group chaned to mqtt
- moved mmh3 to mqtt group
- removed unused imports
- added a determinstic client_id creation when connecting to broker as persisten client (clean_session = false)
- added client_id_suffix to allow multiple clients to conect to a broker from same host with different endings
- self._client needs to be set before call to subscribe
- config anpassungeng für tests
- client_id and clean_session from cli overwrites given config
- added custom client_id in MQTTManager
- added clean_session, client_id and qos to cli
- added client_id
- added clean_session and qos in run_pipieline_on_message command







