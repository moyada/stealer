import subprocess
import time
import logging


# 执行shell命令的方法
# cmd shell命令, timeout 超时：秒
# return （执行状态:int，执行结果:str，执行错误:str）
def run_cmd(cmd, timeout=None):
    try:
        exec_status = -1
        exec_err = ""
        exec_result = ""
        # deprecated，无法提供超时功能
        # exec_status, exec_result = subprocess.getstatusoutput(cmd)

        try:
            # shell=True 因为需要使用通道和字符串子命令，所以默认打开
            with subprocess.Popen(cmd,  shell=True, universal_newlines=True, stderr=subprocess.STDOUT,stdout=subprocess.PIPE) as process:
                # 主要超时控制
                if timeout:
                    to_count = 0
                    while True:
                        # interval sec: 5 因为还有很多long time command，超时间隔不需要太细
                        time.sleep(5)
                        to_count += 5
                        if to_count > timeout:
                            # 回归到subprocess的超时处理
                            process.kill()
                            raise subprocess.TimeoutExpired(process.args, timeout, output=None,
                                             stderr=None)
                        if process.poll() is None:
                            continue
                        else:
                            break

                try:
                    # 完成后获取结果
                    stdout, stderr = process.communicate(input)
                # 此处是subprocess的异常处理，直接使用
                except subprocess.TimeoutExpired:
                    process.kill()
                    stdout, stderr = process.communicate()
                    raise subprocess.TimeoutExpired(process.args, timeout, output=stdout,
                                         stderr=stderr)
                except:
                    process.kill()
                    process.wait()
                    raise
                retcode = process.poll()
                if retcode:
                    raise subprocess.CalledProcessError(retcode, process.args,
                                             output=stdout, stderr=stderr)
                data = subprocess.CompletedProcess(process.args, retcode, stdout, stderr).stdout
                exec_status = 0
        except subprocess.CalledProcessError as ex:
            data = ex.output
            exec_status = ex.returncode
        if data[-1:] == '\n':
            exec_result = data[:-1]

        if exec_status != 0:
            exec_err = exec_result
            exec_result = None
        return exec_status, exec_result, exec_err
    # 自身封装的异常处理，为了记录和返回统一格式
    except subprocess.TimeoutExpired:
        logging.error("cmd:{} is timeout".format(cmd))
        return -9, None, "timeout"
    except BaseException as ose:
        logging.error("cmd:{} error:{}".format(cmd, ose.__str__()))
        return -1, None, ose.__str__()


if __name__ == '__main__':
    print(run_cmd('sh ../video/remd5.sh {} {}'.format('md5', '../video/douyin/3Wok63.mp4')))
