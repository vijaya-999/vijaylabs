AIX Version 7
Copyright IBM Corporation, 1982, 2020.
Console login: root
root's Password: 
********************************************************************************

  IBM Business Use Statement
  --------------------------

    IBM's internal systems must only be used for conducting IBM's business or
    for purposes authorized by IBM management.

    Use is subject to audit at any time by IBM management.

    Highest classification of data allowed on this systems is
    "IBM Confidential"


    HOSTNAME:         pinch08
    BUILD LEVEL:      7.1.5.30
    MODEL/TYPE:       Zeppelin
    ADMINISTRATOR:    Classical Members
    KERNEL INFO:      64BK  
    SETTING INFO:     
    TESTING INFO:     

********************************************************************************



FOCUS TEAMS:    BASE IO NFS NFS_SERVER TCP TCP_SERVER



Last unsuccessful login: Thu Aug 27 00:58:52 CDT 2020 on /dev/pts/0 from loggerbb.isst.aus.stglabs.ibm.com
Last login: Thu Aug 27 00:59:01 CDT 2020 on /dev/pts/0 from loggerbb.isst.aus.stglabs.ibm.com

[root@pinch08] / 
# date; hostname; what /unix | grep build;oslevel
Thu Aug 27 01:05:09 CDT 2020
pinch08
         _kdb_buildinfo unix_64 Aug 25 2020 10:46:09 2035A_71c
7.1.0.0
[root@pinch08] / 
# nohup wrapper.ksh -g BASE IO TCP PROBEVUE & 
[1]     21627048
[root@pinch08] / 
# Sending output to nohup.out

[root@pinch08] / 
# ps -aef | grep wrapper
    root  8192144 24641628   0 01:16:10   vty0  0:00 /usr/bin/ksh /driver/tools/scengen_tcp -d /tmp/wrapper.scendir.082720.010542.21627048 -f ISST_1119.71c.pinch08.m.tcp low
    root 21627048 18153520   0 01:05:42   vty0  0:03 /bin/ksh /driver/tools/wrapper.ksh -g BASE IO TCP PROBEVUE
    root 22282472 21627048  75 01:12:11   vty0  0:02 /usr/bin/ksh /driver/tools/scengen_tcp -d /tmp/wrapper.scendir.082720.010542.21627048 -f ISST_1119.71c.pinch08.m.tcp low
    root 23134388  8192144   0 01:16:10   vty0  0:00 /usr/bin/ksh /driver/tools/scengen_tcp -d /tmp/wrapper.scendir.082720.010542.21627048 -f ISST_1119.71c.pinch08.m.tcp low
    root 24641628 22282472   1 01:16:10   vty0  0:00 /usr/bin/ksh /driver/tools/scengen_tcp -d /tmp/wrapper.scendir.082720.010542.21627048 -f ISST_1119.71c.pinch08.m.tcp low
    root 25755776 18153520   0 01:16:10   vty0  0:00 grep wrapper
[root@pinch08] / 
# 

Broadcast message from root@pinch08 (vty0) at 01:22:41 ... 

wrapper.ksh exit message: Wrapper kicked off successfully with nohup, log file is /tmp/wrapper.pinch08.082720.010544.21627048.5477.25540.log


[1] +  Done                    nohup wrapper.ksh -g BASE IO TCP PROBEVUE &
[root@pinch08] / 
# ps -aef | grep tests
    root 17956892 25034994   1 01:26:18   vty0  0:00 /bin/ksh /driver/tests/io/iozone/bin/iozone
    root 18087978        1   0 00:56:20      -  0:00 /usr/bin/ksh /var/adm/upt/srvd/upt_srvd /driver/tests/tools/bin/upt_srvd_file_tools /driver/tools/upt_rrun_srvd
    root 18808894        1   0 00:56:19      -  0:00 sh -c exec /driver/tests/bloomberg/mbuf_police > /dev/null 2>&1 # Start TCP profile tunables
    root 18874432        1   0 00:56:19      -  0:01 /usr/bin/ksh /var/adm/upt/srvd/upt_srvd /driver/tests/tools/bin/upt_srvd_file_tools /driver/tools/upt_main_srvd
    root 18939970        1  18 00:56:19      -  0:00 /usr/bin/ksh /var/adm/upt/srvd/upt_srvd /driver/tests/tools/bin/upt_srvd_file_tools /driver/tools/upt_focus_srvd
    root 19726376 20185338   0 01:25:16   vty0  0:00 /bin/ksh /driver/tests/io/mpio/bin/mpio
    root 20054094 24641682   0 01:24:37   vty0  0:00 /bin/ksh /driver/tests/tcp/sock_pair/bin/socket_pair
    root 20709476  8192050   0 01:26:21   vty0  0:00 /bin/ksh /driver/tests/tcp/sock_tcp/bin/sock_tcp
    root 22544536 27525278   3 01:26:42   vty0  0:00 dd if=/tmp/io_tests/mpio.t.18219070/file.jmb of=/dev/hdisk4 bs=512
    root 22872240 18939970   0 01:27:18      -  0:00 /usr/bin/ksh /var/adm/upt/srvd/upt_srvd /driver/tests/tools/bin/upt_srvd_file_tools /driver/tools/upt_focus_srvd
    root 23396560 22872240   1 01:27:19      -  0:00 /usr/bin/ksh /var/adm/upt/srvd/upt_srvd /driver/tests/tools/bin/upt_srvd_file_tools /driver/tools/upt_focus_srvd
    root 23593172 19136630   0 01:24:02   vty0  0:00 /bin/ksh /driver/tests/tcp/rlogin/bin/rlogin
    root 23789714 25034994   0 01:26:17   vty0  0:00 /bin/ksh /driver/tests/io/iozone/bin/iozone
    root 24314040 18939970   2 01:27:20      -  0:00 /usr/bin/ksh /var/adm/upt/srvd/upt_srvd /driver/tests/tools/bin/upt_srvd_file_tools /driver/tools/upt_focus_srvd
    root 25034994 22675474   0 01:25:16   vty0  0:00 /bin/ksh /driver/tests/io/iozone/bin/iozone
    root 25165998 19726376   0 01:25:21   vty0  0:00 /bin/ksh /driver/tests/io/mpio/bin/mpio
    root 26345572 18153520   0 01:27:20   vty0  0:00 grep tests
    root 27525278 25165998   0 01:26:42   vty0  0:00 dd if=/tmp/io_tests/mpio.t.18219070/file.jmb of=/dev/hdisk4 bs=512
[root@pinch08] / 
# 

Broadcast message from root@pinch08 (tty) at 01:29:09 ... 

wrapper.ksh: Tests started successfully!


[root@pinch08] / 
# ps -aef | grep tests
    root 17956892 25034994   2 01:26:18   vty0  0:04 /bin/ksh /driver/tests/io/iozone/bin/iozone
    root 18087978        1   0 00:56:20      -  0:00 /usr/bin/ksh /var/adm/upt/srvd/upt_srvd /driver/tests/tools/bin/upt_srvd_file_tools /driver/tools/upt_rrun_srvd
    root 18808894        1   0 00:56:19      -  0:00 sh -c exec /driver/tests/bloomberg/mbuf_police > /dev/null 2>&1 # Start TCP profile tunables
    root 18874432        1   0 00:56:19      -  0:01 /usr/bin/ksh /var/adm/upt/srvd/upt_srvd /driver/tests/tools/bin/upt_srvd_file_tools /driver/tools/upt_main_srvd
    root 18939970        1   0 00:56:19      -  0:00 /usr/bin/ksh /var/adm/upt/srvd/upt_srvd /driver/tests/tools/bin/upt_srvd_file_tools /driver/tools/upt_focus_srvd
    root 19726376 20185338   0 01:25:16   vty0  0:00 /bin/ksh /driver/tests/io/mpio/bin/mpio
    root 23199920 31653950   0 01:36:28   vty0  0:00 /usr/bin/ksh /driver/tests/probevue/probe_evmpagefault/pvstress_evmpagefault.latest -p '300000' -i '1000'
    root 23789714 25034994   0 01:26:17   vty0  0:00 /bin/ksh /driver/tests/io/iozone/bin/iozone
    root 25034994 22675474   0 01:25:16   vty0  0:00 /bin/ksh /driver/tests/io/iozone/bin/iozone
    root 25428060 26017800   1 01:36:35   vty0  0:00 /bin/ksh /driver/tests/tcp/rsh/bin/rsh
    root 29556816 20578486   0 01:29:07   vty0  0:00 /bin/ksh /driver/tests/tcp/sock_tcp/bin/sock_tcp
    root 30539784 24248498   0 01:31:55   vty0  0:00 /bin/ksh /driver/tests/tcp/sock_pair/bin/socket_pair

[root@pinch08] / 
# cd  /STATUS/scripts/eras/probevue/

[root@pinch08] /STATUS/scripts/eras/probevue 
# start_probevue.latest -e racharys@in.ibm.com -T basic -f yes
MAIN LOGS are at : /driver/runtime/eras/pvstress/pinch08/pvstress.log

[root@pinch08] /STATUS/scripts/eras/probevue 
# ps -aef | grep start_probevue.latest
    root 30736424 18153520   1 01:40:52   vty0  0:00 grep start_probevue.latest
	
[root@pinch08] /STATUS/scripts/eras/probevue 
# ps -aef | grep probevue
    root  8192166 22610038   0 01:41:02   vty0  0:00 grep -E probevuejava -classpath
    root 18219150 30998648   0 01:40:47   vty0  0:00 /bin/ksh /driver/runtime/probevue/ISST_1119.71c.pinch08.m.probevue.pinch08.root.20200827.012745.163/probevue/tfiles/evmpagefault.t.pinch08.evmpagefault.pinch08/20200827.014045.735.1/014045805
    root 19857480 29163694   4 01:41:01   vty0  0:00 ksh /STATUS/scripts/eras/probevue/tprobev.lp.ptree.gst -z -s -T -l -a -K -N -t 3601100 -S /tmp/pvstress_threaded/pinch08.0827.0139.29163694/threaded.e -O /tmp/pvstress_threaded/pinch08.0827.0139.29163694/threaded64.probevue.log -A -t 16 -X /tmp/pvstress_threaded/pinch08.0827.0139.29163694/threaded_64
    root 20054194        1   0 01:39:01   vty0  0:00 /usr/bin/ksh /STATUS/scripts/eras/probevue/pvstress_ps_process.latest -p 10000 -i 3600000 -t tprobev.lp.ptree.gst
    root 21889208 24051838 114 01:40:10   vty0  0:04 probevue ./probe_syscallx_commit.e.lp 12
    root 21954594 24117498   2 01:41:02   vty0  0:00 /bin/sh /STATUS/scripts/eras/probevue/probe_cplus/tplate.sh 1 tfile24117498
    root 22216762        1   0 01:38:21   vty0  0:00 /usr/bin/ksh /STATUS/scripts/eras/probevue/probe_cplus/pvstress_cplus.latest -p 10000 -i 3600000 -t tprobev.lp.ptree.gst
    root 22610038        1   6 01:39:21   vty0  0:00 /bin/ksh /STATUS/scripts/eras/probevue/pvstress_java.latest
    root 24051838        1  15 01:38:41   vty0  0:00 /usr/bin/ksh /STATUS/scripts/eras/probevue/probe_syscallx/pvstress_syscallx.latest -p 10000 -i 3600000
    root 25690230 21954594   4 01:41:02   vty0  0:00 /bin/ksh /STATUS/scripts/eras/probevue/probe_cplus/buildallcomb
    root 25755808 18219150   0 01:40:47   vty0  0:00 /usr/bin/ksh /driver/tests/probevue/probe_evmpagefault/pvstress_evmpagefault.latest -p '300000' -i '1000'
    root 25952410 31260766   0 01:27:44   vty0  0:00 /driver/java5/jre/bin/java -Xmx128m -Xms32m ATP -p /driver/dat/atp.cfg.db -status ISST_1119.71c.pinch08.m.probevue
    root 26869814        1   0 01:38:31   vty0  0:00 /usr/bin/ksh /STATUS/scripts/eras/probevue/probe_evmpagefault/pvstress_evmpagefault.latest -p 10000 -i 3600000
    root 28377218 18153520   0 01:41:02   vty0  0:00 grep probevue
    root 28901618        1   0 01:27:45   vty0  0:00 /driver/java5/jre/bin/java -mx128m ATPStatus -p /driver/dat/atp.cfg.db -initial -focus probevue ISST_1119.71c.pinch08.m.probevue.pinch08.root.20200827.012745.163
    root 29163694        1   0 01:39:31   vty0  0:00 /usr/bin/ksh /STATUS/scripts/eras/probevue/probe_threaded_binary/pvstress_threaded.latest -p 10000 -i 3600000 -t tprobev.lp.ptree.gst
    root 29687870 24051838   0 01:41:02   vty0  0:00 grep probevue ./probe_syscallx
    root 30474288 19857480 101 01:41:02   vty0  0:00 probevue -u -o /tmp/pvstress_threaded/pinch08.0827.0139.29163694/threaded64.probevue.log -I /STATUS/scripts/eras/probevue/kernel.h -X /tmp/pvstress_threaded/pinch08.0827.0139.29163694/threaded_64 -A -t 16 /tmp/pvstress_threaded/pinch08.0827.0139.29163694/threaded.e 3601100 >/dev/null 2>>/tmp/pvstress_threaded/pinch08.0827.0139.29163694/threaded64.tprobev_error.log
    root 30998648 25952410   0 01:40:45   vty0  0:00 /bin/ksh /driver/runtime/probevue/ISST_1119.71c.pinch08.m.probevue.pinch08.root.20200827.012745.163/probevue/tfiles/evmpagefault.t.pinch08.evmpagefault.pinch08/20200827.014045.735.1/014045805
    root 31260766        1   0 01:27:44   vty0  0:00 /usr/bin/ksh -c  /driver/bin/atp -p /driver/dat/atp.cfg.db -status ISST_1119.71c.pinch08.m.probevue  
	
[root@pinch08] /STATUS/scripts/eras/probevue 
# ps -aef | grep test
    root 17956892 25034994   8 01:26:18   vty0  0:07 /bin/ksh /driver/tests/io/iozone/bin/iozone
    root 18087978        1   0 00:56:20      -  0:00 /usr/bin/ksh /var/adm/upt/srvd/upt_srvd /driver/tests/tools/bin/upt_srvd_file_tools /driver/tools/upt_rrun_srvd
    root 18808894        1   0 00:56:19      -  0:00 sh -c exec /driver/tests/bloomberg/mbuf_police > /dev/null 2>&1 # Start TCP profile tunables
    root 18874432        1   0 00:56:19      -  0:01 /usr/bin/ksh /var/adm/upt/srvd/upt_srvd /driver/tests/tools/bin/upt_srvd_file_tools /driver/tools/upt_main_srvd
    root 18939970        1   0 00:56:19      -  0:00 /usr/bin/ksh /var/adm/upt/srvd/upt_srvd /driver/tests/tools/bin/upt_srvd_file_tools /driver/tools/upt_focus_srvd
    root 20054194        1   0 01:39:01   vty0  0:00 /usr/bin/ksh /STATUS/scripts/eras/probevue/pvstress_ps_process.latest -p 10000 -i 3600000 -t tprobev.lp.ptree.gst
    root 20119754 21233810   0 01:38:56   vty0  0:00 /bin/ksh /driver/tests/tcp/sock_pair/bin/socket_pair
    root 22216762        1   0 01:38:21   vty0  0:00 /usr/bin/ksh /STATUS/scripts/eras/probevue/probe_cplus/pvstress_cplus.latest -p 10000 -i 3600000 -t tprobev.lp.ptree.gst
    root 22610038        1   0 01:39:21   vty0  0:00 /bin/ksh /STATUS/scripts/eras/probevue/pvstress_java.latest
    root 23789714 25034994   0 01:26:17   vty0  0:00 /bin/ksh /driver/tests/io/iozone/bin/iozone
    root 24051838        1   8 01:38:41   vty0  0:00 /usr/bin/ksh /STATUS/scripts/eras/probevue/probe_syscallx/pvstress_syscallx.latest -p 10000 -i 3600000
    root 25034994 22675474   0 01:25:16   vty0  0:00 /bin/ksh /driver/tests/io/iozone/bin/iozone
    root 25100442 25821208   0 01:37:12   vty0  0:00 /bin/ksh /driver/tests/tcp/sock_tcp/bin/sock_tcp
    root 25755808 18219150   0 01:40:47   vty0  0:00 /usr/bin/ksh /driver/tests/probevue/probe_evmpagefault/pvstress_evmpagefault.latest -p '300000' -i '1000'
    root 26869814        1   0 01:38:31   vty0  0:00 /usr/bin/ksh /STATUS/scripts/eras/probevue/probe_evmpagefault/pvstress_evmpagefault.latest -p 10000 -i 3600000
    root 27721972 29229168   0 01:37:53   vty0  0:00 /bin/ksh /driver/tests/tcp/rlogin/bin/rlogin
    root 28704902 29819132   5 01:40:37   vty0  0:00 /bin/ksh /driver/tests/io/mir_stripe/bin/mir_stripe
    root 29163694        1   0 01:39:31   vty0  0:00 /usr/bin/ksh /STATUS/scripts/eras/probevue/probe_threaded_binary/pvstress_threaded.latest -p 10000 -i 3600000 -t tprobev.lp.ptree.gst
    root 31129726 18153520   1 01:41:14   vty0  0:00 grep test
	
[root@pinch08] /STATUS/scripts/eras/probevue 
# errpt | head
IDENTIFIER TIMESTAMP  T C RESOURCE_NAME  DESCRIPTION
AA8AB241   0827012720 T O OPERATOR       OPERATOR NOTIFICATION
AA8AB241   0827012620 T O OPERATOR       OPERATOR NOTIFICATION
AA8AB241   0827012520 T O OPERATOR       OPERATOR NOTIFICATION
AA8AB241   0827012420 T O OPERATOR       OPERATOR NOTIFICATION
BFE4C025   0827005720 P H sysplanar0     UNDETERMINED ERROR
BFE4C025   0827005720 P H sysplanar0     UNDETERMINED ERROR
DE84C4DB   0827005620 I O ConfigRM       IBM.ConfigRM daemon has started. 
A6DF45AA   0827005620 I O RMCdaemon      The daemon is started.
AA8AB241   0827005620 T O OPERATOR       OPERATOR NOTIFICATION
