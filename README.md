# Modeling a fault-tolerant geo-distributed network infrastructure

## INTRODUCTION
Any modern enterprise, regardless of its scale, cannot perform successfully on a market without usage of information systems and business critical services which are running on top of complex IT infrastructure. The more opportunities and agility an IT infrastructure provide for automating business processes, the more difficult and complex it becomes.

It is obvious, that modern IT infrastructure challenges require modern tools and solutions to meet business objectives. Some of such modern tools enable engineers to run production-like infrastructure simulations to develop, test and assess changes and new approaches build a brand-new infrastructure deployment or examine how existing deployment can be extended using IaaS offerings and hybrid infrastructure methodologies.

## TEST PROJECT OVERVIEW
**SkillsCloud Company** is the leader in the API development for SCADA systems data analysis market. This year, company finished migration of their solutions to a public cloud but still, there are some cases when SkillsCloud API must be integrated with customers’ on-premises infrastructure, in order to comply with local regulations.

In 2021, **Chemisch Thermische Prozesstechnik GmbH (CTP)** plans to implement a project to integrate local SCADA monitoring with SkillsCloud data processing engines. To achieve this goal, CTP negotiating a separate infrastructure that will be responsible for collecting and storing SCADA data to make a secure, scalable and fault-tolerant solution that allows data exchange between local data collection systems and the SkillsCloud API.

Within current project, your team is responsible to implement a simulated infrastructure scenario according to initial design and industry best practices.

## INSTRUCTIONS TO THE COMPETITOR
*	Initial topology will be pre-built and read-only access to this topology will be granted to each team using infrastructure simulation platform. Teams will be able to run and configure VMs but will not be able to change topology layout. All ISP devices will be running on the separate shared tenant and will not be accessible by teams.

*	Test project marking process will be fully automated, so make sure that following credentials policy is respected:
    * Default user: **admin** (Linux and Cisco VMs)
    * Default password: **Passw0rd!**

*	Save your configurations frequently and make sure that all your configurations are still working as expected after equipment rebooting. Before you will submit your work, make sure that all configuration also saved inside topology file as well.

*	Implement all tasks to the best of your ability, in line with **industry best practices** (in terms of security, high availability and scalability) within the limitations imposed by software images used.


## TEST PROJECT GUIDELINES
Examine initial and desired state of the infrastructure for CTP and SkillsCloud Company. Implement all required configuration to meet basic reachability requirements, which can be found at the end of this document. Note that simulated public cloud providers do not allow GRE traffic (IP/47) to traverse inside their networks.

Make sure that all reachability conditions are still met in event of any redundant component failure (server links, core switches, edge routers, on-premises internet service providers) in various combinations.  Duration of connectivity loss might not be longer than 10 seconds. 

## INITIAL STATE
![Network infrastructure case](diagrams/initial_state.png)

## DESIRED STATE
![Subnetting map](diagrams/desired_state.png)

## RECHABILITY REQUIREMENTS

|:arrow_down_small:SRC/DST:arrow_forward:|Sandbox|SCADA|Operations|AWS-VPC|AZR-VPC|GCP-VPC|Cloudflare|
|----------|:-----:|:---:|:--------:|:-----:|:-----:|:-----:|:-----:|
|**Sandbox**   |:heavy_check_mark:|:x:|:leftwards_arrow_with_hook:|:x:|:x:|:x:|:globe_with_meridians:|
|**SCADA**     |:x:|:x:|:leftwards_arrow_with_hook:|:globe_with_meridians:|:globe_with_meridians:|:globe_with_meridians:|:x:|
|**Operations**|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|
|**AWS-VPC**   |:x:|:x:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:globe_with_meridians:|
|**AZR-VPC**   |:x:|:x:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:globe_with_meridians:|
|**GCP-VPC**   |:x:|:x:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:heavy_check_mark:|:globe_with_meridians:|

|Legend|Action|
|:---:|-----|
|:heavy_check_mark:|Allow all traffic|
|:x:|Deny all traffic|
|:leftwards_arrow_with_hook:|Allow return traffic only|
|:globe_with_meridians:|Allow web traffic only|
