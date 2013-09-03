#!/usr/bin/python
#-*-coding:utf8-*-
import sys, time, pexpect, os, re, codecs
import logging
import traceback

class RemoteCommander:
   
    @staticmethod
    def runCommand(user, host, password, cmd):
        """
        This runs a command on the remote host. This could also be done with the
        pxssh class, but this demonstrates what that class does at a simpler level.
        This returns a pexpect.spawn object. This handles the case when you try to
        connect to a new host and ssh asks you if you want to accept the public key
        fingerprint and continue connecting.
        """
        msg = "run command %s in %s@%s using passwd %s"%(cmd, user,host, password)
        try:
            ssh_newkey = 'Are you sure you want to continue connecting'
            # 为 ssh 命令生成一个 spawn 类的子程序对象.
            child = pexpect.spawn('ssh -l %s %s %s'%(user, host, cmd))
            i = child.expect([pexpect.TIMEOUT, ssh_newkey, 'password: '])
            # 如果登录超时，打印出错信息，并退出.
            if i == 0: # Timeout
                logging.warn( '[%s] SSH could not login. Here is what SSH said: [%s], [%s]'%(msg, child.before, child.after) )
                return (False, "")
            # 如果 ssh 没有 public key，接受它.
            if i == 1: # SSH does not have the public key. Just accept it.
                child.sendline ('yes')
                #child.expect ('password: ',timeout = 2)
                i = child.expect([pexpect.TIMEOUT, 'password: '], timeout=3)
                if i == 0: # Timeout
                    logging.warn( '[%s] SSH could not login. Here is what SSH said: [%s], [%s]'%(msg, child.before, child.after) )
                    return (False, "")
            # 输入密码.
            child.sendline(password)
            i = child.expect(pexpect.EOF)
            if i == 0:
                return (True, child.before)
            else:
                return (False, "")
                logging.warn( '[%s] SSH could not login. Here is what SSH said: [%s], [%s]'%( msg, child.before, child.after) )
        except:
            logging.error("[[\n%s\n]]"%(traceback.format_exc()))
            logging.warn("[%s] wrong"%msg)
            return (False, "")

    @staticmethod
    def getMD5(data):
        dict = {}
        data_info = data.split("\n")
        for item in data_info:
            item = item.strip()
            if cmp(item, "") == 0:
                continue
            info = item.split()
            if len(info) == 2:
                dict[info[0]] = info[1]
        return dict

    @staticmethod
    def scp(srcFile,  user, host, destFile, passwd, dir_exits=False):
        '''将srcFile 拷贝到user@host:destFile 密码是passwd,
        dir_exits == False 目标文件必须不存在
        '''
        #check if file exists
        (flag, data) = RemoteCommander.runCommand(user, host, passwd, "ls " + destFile)
        if data.find( "cannot access") == -1 and dir_exits == False:
            logging.error( destFile + " already exist in %s@%s"%(user, host))
            return False
        scpCmd = 'scp -r %s %s@%s:%s' % (srcFile, user, host, destFile)
        logging.info(scpCmd)
        ch = pexpect.spawn(scpCmd)
        try:
            ind = ch.expect(["'s password: ", "continue connecting (yes/no)?"], timeout=20)
            if ind == 1:
                ch.sendline("yes");
                ch.expect(["'s password: "], timeout=20)
            ch.sendline(passwd)
            i = ch.expect([pexpect.TIMEOUT, pexpect.EOF], timeout=60)
            if i == 0:
                logging.warn("scp time out[%s] "%scpCmd )
                return False
        except Exception as e:
            logging.error("[[\n%s\n]]"%(traceback.format_exc()))
            logging("[%s] wrong"%(scpCmd))
            return False
        '''
        检查完整性
        '''
        current = os.popen("find %s   -type f   | xargs md5sum" %(srcFile)).read()
        dict_source = RemoteCommander.getMD5(current)
        remote_command = "find %s  -type f | xargs md5sum  " %(destFile)
        (flag, data) = RemoteCommander.runCommand(user, host, passwd, remote_command)
        dict_target = RemoteCommander.getMD5(data)
        diff = set(dict_source.keys() ) - set(dict_target.keys())
        if len(diff) > 0 :
            logging.error(scpCmd + " not integrity")
            return False
        return True




if __name__=="__main__":
    targetfile = sys.argv[1]
    (flag, data) = RemoteCommander.runCommand("search", "192.168.23.50", "search", " ls /home ")
    print flag
    print RemoteCommander.scp("/tmp/z", "taozw", "192.168.23.209", targetfile, "taozw")
