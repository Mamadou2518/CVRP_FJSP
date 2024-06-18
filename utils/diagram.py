import numpy
import matplotlib.pyplot as plt
import math
import matplotlib

class diagram:
    def __init__(self,NM,NJ,PMT,lamda,mu,cmax,schedule,maint,ehf,pngfname,showgantt,showehf):
        self.NM = NM
        self.NJ = NJ
        self.PMT = PMT
        self.lamda = lamda
        self.mu = mu
        self.cmax = cmax
        self.schedule = schedule
        self.maint = maint
        self.ehf = ehf
        self.ganttsavefilename = f"{pngfname}_pmt{PMT}-lambda{lamda}-mu{mu}_gantt.png"
        self.ehfplotsavefilename = f"{pngfname}_pmt{PMT}-lambda{lamda}-mu{mu}_ehf.png"
        self.mcolors = [
            'tab:red', 'tab:cyan', 'tab:green', 'tab:orange', 'tab:grey', 'yellow', 
            'tab:brown', 'magenta', 'lime', 'tomato', 'tab:blue', 'red', 'cyan', 
            'green', 'blue','khaki','violet','gold','olivedrab','thistle'
        ]
        self.showG = showgantt
        self.showEHF = showehf
        self.pngfname = pngfname
        
    def plotGantt(self):
        fig, gnt = plt.subplots(figsize=(20, 10)) 
        gnttitle = f"schedule {self.pngfname} $\lambda^{{PM}}$={self.lamda} $\mu$={self.mu} PMT={self.PMT}"
        plt.title(gnttitle, fontsize=25) 
        gnt.minorticks_on()
        gnt.grid(which='major', linestyle='-', linewidth='0.5', color='grey')
        gnt.grid(which='minor', linestyle=':', linewidth='0.5', color='grey')
        gnt.set_ylim(0, 10 * (1+self.NM))
        gnt.set_xlim(0, self.cmax)
        gnt.set_xlabel('Time', fontsize=24, weight='bold')
        gnt.set_ylabel('Processors', fontsize=24, weight='bold')
        gnt.tick_params(labelsize=22)
        yticks = [10 * (m + 1) for m in range(self.NM)]
        gnt.set_yticks(yticks)
        ylabels = [f'M{m+1}' for m in range(self.NM)]
        gnt.set_yticklabels(ylabels, fontsize=20)
        
        for m in range(self.NM):
            a = []
            b = ()
            for task in self.schedule[m]:
                a.append((task[2], task[3]-task[2]))
                b = b + (self.mcolors[task[0]],)
                op = f'$\\_({task[0]},{task[1]})$'
                x = task[2] + 0.1
                y = yticks[m]
                gnt.text(x, y, op, fontsize=20, weight='bold')   
            if len(self.maint[m]) > 0:
                for mtask in self.maint[m]:
                    a.append((mtask[0], self.PMT))
                    b = b + ('black',)
            gnt.broken_barh(a, (yticks[m]-2, 4), facecolors=b)
        
        patches = [matplotlib.patches.Patch(color=self.mcolors[j]) for j in range(self.NJ)]
        jobkeys = [f'Job {j}' for j in range(self.NJ)]
        if any(len(m) for m in self.maint):
            print("/!\ some maintenance tasks are planned !")
            jobkeys.append('PdM')
            patches.append(matplotlib.patches.Patch(color='black')) 
        plt.legend(handles=patches, labels=jobkeys, fontsize=15)
        fig.savefig(self.ganttsavefilename, bbox_inches='tight')
        if not self.showG:
            plt.close(fig)

    def plotEHF2(self):
        EHF = numpy.zeros((self.NM, self.cmax+1))
        for m in range(self.NM):
            MT = [Mtask[0] for Mtask in self.maint[m]]
            for tid, task in enumerate(self.schedule[m]):
                if tid == 0:
                    for t in range(task[2]+1):
                        EHF[m][t] = 0
                for t in range(task[2]+1, task[3] + 1):
                    if t <= self.cmax:
                        EHF[m][t] = EHF[m][t - 1] + self.mu
                if tid < len(self.schedule[m]) - 1:
                    for t in range(task[3]+1, self.schedule[m][tid + 1][2]+1):
                        if t-1 in MT:
                            EHF[m][t] = 0
                        else:
                            EHF[m][t] = EHF[m][t - 1]
                else:
                    if task[3] < self.cmax:
                        for t in range(task[3] + 1, self.cmax+1):
                            EHF[m][t] = EHF[m][t - 1]
        
        maxehf = max([max(ehf) for ehf in EHF])
        fig, ehf = plt.subplots(nrows=self.NM, ncols=1, figsize=(20, 15))
        plt.suptitle(f"EHF {self.pngfname} $\mu$={self.mu} PMT={self.PMT}", fontsize=25)
        for m in range(self.NM):
            m0 = self.NM - m - 1
            mlabel = f'M{m0+1}'
            ehf[m].minorticks_on()
            ehf[m].grid(which='major', linestyle='-', linewidth='0.5', color='grey')
            ehf[m].grid(which='minor', linestyle=':', linewidth='0.5', color='grey')
            ehf[m].set_ylim(-0.1, maxehf+0.1)
            ehf[m].set_xlim(0, self.cmax)
            if m < self.NM - 1:
                plt.setp(ehf[m].get_xticklabels(), visible=False)
            if m == self.NM - 1:
                ehf[m].set_xlabel('Time', fontsize=20, weight='bold')
            ehf[m].set_ylabel(mlabel, fontsize=20, weight='bold')
            ehf[m].tick_params(labelsize=22)
            ehf[m].plot(0, 0, "b^")
            for t in range(1, math.ceil(self.cmax)+1):
                ehf[m].plot(t, EHF[m0][t], "b^")
                if t < self.cmax - 1:
                    if EHF[m0][t + 1] < EHF[m0][t]:
                        ehf[m].text(t, EHF[m0][t] + 0.05, r'%.2f' % EHF[m0][t], fontsize=15)
                    if t > 1 and EHF[m0][t - 1] < EHF[m0][t] and EHF[m0][t + 1] == EHF[m0][t]:
                        ehf[m].text(t, EHF[m0][t] + 0.05, r'%.2f' % EHF[m0][t], fontsize=15)
                else:
                    ehf[m].text(t, EHF[m0][t] + 0.05, r'%.2f' % EHF[m0][t], fontsize=15)
            ehf[m].plot(range(math.ceil(self.cmax)+1), [EHF[m0][t] for t in range(math.ceil(self.cmax)+1)], color="b", ls="--")
        fig.savefig(self.ehfplotsavefilename)
        if not self.showEHF:
            plt.close(fig)
        return EHF
