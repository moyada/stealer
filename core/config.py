import os

base_path = os.getcwd() + "/video/"

web_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
sec_ua = "\"Not_A_Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\""
user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"

dy_cookie = "douyin.com; webcast_local_quality=null; __ac_referer=__ac_blank; d_ticket=954b3cdbf9f3c5f7b1c2ff1ba5173f887f6a6; n_mh=eC2nr3EWmL8R9UPlHOVk5uazNPrMum-0VC0m9OcQC9Y; store-region=cn-fj; store-region-src=uid; LOGIN_STATUS=0; odin_tt=1c94a7a4625315190f50045bc504c1a8064e372100876518a32c547876a7e8dfd4d49217594a47341d57e232062a3462cead12ad1bd7bed9fa1430fc9a11176a; xgplayer_user_id=689542287459; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%2C%22isForcePopClose%22%3A1%7D; s_v_web_id=verify_ljn1xtoc_tYEclCsb_m8Xl_4fb7_Bzfl_EGccLrMo3CkT; passport_csrf_token=5d5dca2c0c370ab1aca1b42dffe6f1a6; passport_csrf_token_default=5d5dca2c0c370ab1aca1b42dffe6f1a6; ttwid=1%7CSPH7XdmGcnwzjGcJDbz2XeJloqAM6fpd6osS3Ch5y_U%7C1690817288%7C9a5c63731028fcb21ee736c1f7119dabc1c45698fa14e0fcd06489d4cbb6f971; download_guide=%223%2F20230819%2F1%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCRHV3SjQyV1EyMTFGbDBMYlNEbzU0S1JnR2ZVcU9mZmkyOVkvUm1wL0R1MDUxN2V5QmxwMlVnTkhzaDlPUnN4bU16dWZ1cUVpeGZhVmtGZFVUOEY2WGM9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ==; pwa2=%220%7C0%7C3%7C0%22; SEARCH_RESULT_LIST_TYPE=%22single%22; __live_version__=%221.1.1.3293%22; live_can_add_dy_2_desktop=%221%22; douyin.com; device_web_cpu_core=8; device_web_memory_size=8; webcast_local_quality=null; csrf_session_id=a3b6650e0382e37ebebcc34420198f16; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Afalse%2C%22volume%22%3A1%7D; strategyABtestKey=%221693506803.201%22; VIDEO_FILTER_MEMO_SELECT=%7B%22expireTime%22%3A1694144585836%2C%22type%22%3A1%7D; __ac_nonce=064f18b64006a53d9da57; __ac_signature=_02B4Z6wo00f0182SW2gAAIDAneUfk4POQqfNsl.AAJeeTbFu3.Az.5A95FBrVESkLeoOGBOcexJE4ojWnPyS0ddJ7kq9xNzb-Nzq21JHt8kByu4BspmIXZWb0tAaP1ybRCwX44EJq6sV2npR71; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1920%2C%5C%22screen_height%5C%22%3A1080%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A8%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22; home_can_add_dy_2_desktop=%221%22; msToken=LCbCR_2xF7fuEsQCggf0NSzsiUIvQyX0RR7ho_yqpZCQOAc12fqFArTVml4q-ydBig8K4wkp1lhv6ib8kOBUSgmxk2whnczCbABBkmpYxXzWsJKdgqNBT_wKvlvNAow=; msToken=ihpXYiCUYQk4euK5BXf7mOSrwRoxsCCF13st-OM3L1SYbhGzxrdhWkz02EeoAzwh8kB6y-nN_8OyJb3XoOO6eAzW-F-frMufYqRaUX_jkgktm4DF2paq8Q==; tt_scid=DaZU3sAU14kbgMDue3PpZ6Mzec6B.Yt.aEGRTLsIWtP25pFx9xf3F5O5gZoSTnsA64b2; IsDouyinActive=false"

# cookie from https://api.bilibili.com/xxx
bilibili_cookie = ""

env_bc = os.environ.get('BILIBILI_COOKIE')
if env_bc:
    bilibili_cookie = env_bc

os.environ['page_wait'] = "5000"
os.environ['headless']  = "1"