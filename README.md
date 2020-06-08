# StateSim: Monte Carlo simulation of international state systems

Python simulation of war and diplomacy. 

The paper uses a computer simulation to shed light on contradictory hypotheses generated from the realist school of international relations. It draws on the work of Cusack and Stoll (1990b). The simulation initializes 98 primitive states, modeled as random regular graph. The states ally with and fight wars against eachother, governed by simulation parameters set by the researcher. The parameters control variables like presence of norms of restraint, distribution of power, accuracy of perception, destructiveness of wars, the weight of chance in deciding outcome of combat, etc.

Nearly 1600 simulations were ran and recorded (`data` folder). Parametric survival analysis is used to adjudicate between competing theories. The results are broadly consistent with Cusack and Stoll in that key variables are shown to be statistically significant, refuting ‘automatic stabilization’ theories of state systems. See the pdfs in the `paper` directory.

The simulation begins with initialization:

* Phase I: Initialize data and build world

Proceeds in _n_ iterations (in the paper, 1000), each in three phases:

* Phase II: Diplomacy
* Phase III: War (potentially)
* Phase IV: Power adjustment



## References

This project is heavily inspired by some literature developed in the late 1980s and early 1990s, by Richard J. Stoll, Thomas R. Cusack, and a few others. Their work was in turn based on an even older computer simulation due to Bremer and Mihakla (1977). Cusack (1990) contains an overview of the research program.

* Bremer, S., and M. Mihakla. 1977. “Machievalli in Machina: Or politics among hexagons.” In _Problems of World Modeling_, ed. K.W. Deutsch, et al. Ballinger.

* Cusack, Thomas R. 1988. “The management of power in
a warring state system: An evaluation of balancing, collective security and laissez-faire politics.” WZB Discussion Paper, No. P 88-303. Wissenschaftszentrum Berlin fur Sozialforschung (WZB), Berlin, West Germany. Available at https://www.econstor.eu/bitstream/10419/77607/1/670393525.pdf.

* ———. 1990. “Realpolitik and multistate system stability.” WZB Discussion Paper, No. P 90-308. Wissenschaftszentrum Berlin fur Sozialforschung (WZB), Berlin, Germany. Available at http://hdl.handle.net/10419/77609/.

* Cusack, Thomas R., and Richard J. Stoll. 1990a. “Adaptation, state survival and system endurance: A simulation study.” _International Political Science Review_ vol. 11, no. 2: 261–78.

* ———. 1990b. _Exploring Realpolitik: Probing International Relations Theory with Computer Simulation_. Lynne Rienner Publishers.

* Cusack, Thomas R., and Uwe Zimmer. 1989. “Realpolitik and the bases of multistate system endurance.” _Journal of Politics_ vol. 51, no. 2: 247-85.

* Duffy, Gavan. 1992. “Concurrent interstate conflict simulations: Testing the effects of the serial assumption.” _Mathematical and Computer Modelling_ vol. 16, no. 8–9: 241–70.

* Stoll, Richard J. 1987. “System and state in international politics: A computer simulation of balancing in an anarchic world.” _International Studies Quarterly_ vol. 31: 387–402.

