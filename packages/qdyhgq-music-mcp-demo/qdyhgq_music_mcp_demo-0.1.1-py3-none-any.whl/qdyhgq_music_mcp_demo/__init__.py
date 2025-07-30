from mcp.server.fastmcp import FastMCP
import requests
import os
import logging
import threading
import pygame  # 替换playsound库
import re
import time
import sys

# 初始化MCP和日志
mcp = FastMCP("CustomMusicPlayer")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
_LOCK = threading.Lock()  # 保留原线程锁

_API_URL = 'https://api.yaohud.cn/api/music/wy'
_API_KEY = 'pXnLhoquMOnnpcp90JJ'

# _API_URL = 'https://wanghun.top/api/mirai/wy.php'
# _API_KEY = 'pXnLhoquMOnnpcp90JJ'

# 全局变量，用于控制播放状态
_CURRENT_SONG = None
_IS_PLAYING = False
_PLAYER_INITIALIZED = False
_CURRENT_LYRICS = []  # 存储当前歌曲的歌词数据
_LYRICS_THREAD = None  # 歌词显示线程
_STOP_LYRICS = False  # 控制歌词显示停止

# 解析歌词文本，提取时间戳和歌词内容
def parse_lyrics(lrc_text):
    """
    解析LRC格式的歌词
    Args:
        lrc_text: LRC格式的歌词文本
    Returns:
        list: 包含(时间戳秒数, 歌词内容)的元组列表，按时间排序
    """
    lyrics = []
    if not lrc_text:
        return lyrics

    # 正则表达式匹配时间戳格式 [mm:ss.xx]
    pattern = r'\[(\d{2}):(\d{2})\.(\d{2})\](.*)'

    for line in lrc_text.split('\n'):
        match = re.match(pattern, line.strip())
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            centiseconds = int(match.group(3))
            text = match.group(4).strip()

            # 转换为总秒数
            total_seconds = minutes * 60 + seconds + centiseconds / 100.0

            if text:  # 只添加非空歌词
                lyrics.append((total_seconds, text))

    # 按时间排序
    lyrics.sort(key=lambda x: x[0])
    return lyrics

# 显示歌词的线程函数
def display_lyrics_thread():
    """在单独线程中显示歌词"""
    global _STOP_LYRICS, _CURRENT_LYRICS

    if not _CURRENT_LYRICS:
        logger.warning("歌词数据为空，无法显示")
        return

    start_time = time.time()
    current_index = 0

    logger.info("开始显示歌词...")

    # 使用stderr输出，确保在MCP环境中可见
    sys.stderr.write("\n" + "="*50 + "\n")
    sys.stderr.write("🎵 歌词显示 🎵\n")
    sys.stderr.write("="*50 + "\n")
    sys.stderr.flush()

    while not _STOP_LYRICS and current_index < len(_CURRENT_LYRICS):
        current_time = time.time() - start_time

        # 检查是否到了显示下一行歌词的时间
        if current_index < len(_CURRENT_LYRICS):
            timestamp, lyric = _CURRENT_LYRICS[current_index]

            if current_time >= timestamp:
                # 显示当前歌词
                sys.stderr.write(f"🎤 {lyric}\n")
                sys.stderr.flush()
                # logger.info(f"显示歌词: {lyric}")
                current_index += 1

        time.sleep(0.1)  # 每100ms检查一次

    if not _STOP_LYRICS:
        sys.stderr.write("="*50 + "\n")
        sys.stderr.write("🎵 歌词结束 🎵\n")
        sys.stderr.write("="*50 + "\n\n")
        sys.stderr.flush()
        logger.info("歌词显示结束")

# 初始化pygame混音器
def init_pygame():
    global _PLAYER_INITIALIZED
    if not _PLAYER_INITIALIZED:
        pygame.mixer.init()
        _PLAYER_INITIALIZED = True
        logger.info("Pygame混音器已初始化")

@mcp.tool()
def playMusic(song_name: str, id: str = '100') -> str:
    """
    通过MCP接口播放音乐（线程安全）
    Args:
        song_name: 歌曲名
        id: 唯一标识（可用于追踪调用，默认100）
    Returns:
        str: 播放结果或错误信息
    """
    global _CURRENT_SONG, _IS_PLAYING, _CURRENT_LYRICS, _LYRICS_THREAD, _STOP_LYRICS

    if not song_name.strip():
        return "错误：歌曲名不能为空"

    with _LOCK:
        try:
            # 初始化pygame
            init_pygame()

            # 如果当前有音乐在播放，先停止
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                logger.info("停止当前播放的音乐")

            # 1. 调用API获取音乐URL，支持重试机制
            logger.info(f"搜索歌曲: {song_name}")
            music_url = None
            max_retries = 10  # 最大重试次数

            for n in range(1, max_retries + 1):
                try:
                    logger.info(f"尝试搜索 (第{n}次): {song_name}")
                    params = {'key': _API_KEY, 'msg': song_name.strip(), 'n': str(n)}
                    resp = requests.post(_API_URL, params=params, timeout=10)
                    resp.raise_for_status()

                    response_data = resp.json()
                    music_url = response_data.get('data', {}).get('musicurl', '')

                    # 检查URL是否有效
                    if music_url and music_url.strip() and music_url != 'null' and music_url != 'None':
                        logger.info(f"找到有效音乐URL (第{n}次尝试): {music_url}")

                        # 获取歌词数据
                        lyrics_data = response_data.get('data', {}).get('lrctxt', {}).get('data', '')
                        if lyrics_data:
                            _CURRENT_LYRICS = parse_lyrics(lyrics_data)
                            logger.info(f"成功解析歌词，共{len(_CURRENT_LYRICS)}行")
                            # 调试：显示前几行歌词
                            if _CURRENT_LYRICS:
                                logger.info(f"第一行歌词: {_CURRENT_LYRICS[0]}")
                                if len(_CURRENT_LYRICS) > 1:
                                    logger.info(f"第二行歌词: {_CURRENT_LYRICS[1]}")
                        else:
                            _CURRENT_LYRICS = []
                            logger.info("未找到歌词数据")

                        break
                    else:
                        logger.warning(f"第{n}次尝试获取的URL无效: {music_url}")
                        music_url = None

                except Exception as e:
                    logger.warning(f"第{n}次API调用失败: {str(e)}")
                    music_url = None

            # 如果所有重试都失败，返回错误
            if not music_url:
                return f"搜索失败：尝试了{max_retries}次都无法找到有效的音乐链接"

            # 2. 下载并保存文件
            music_dir = "/Users/chablino/Localcode/xiaozhiMCP/xiaozhi-mcp-music/music"
            os.makedirs(music_dir, exist_ok=True)
            music_path = os.path.join(music_dir, f"{song_name}.mp3")

            with open(music_path, 'wb') as f:
                f.write(requests.get(music_url, timeout=10).content)

            logger.info(f"音乐文件保存在: {music_path}")

            # 3. 使用pygame播放音乐
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play()

            # 更新全局状态
            _CURRENT_SONG = song_name
            _IS_PLAYING = True

            # 4. 启动歌词显示线程
            _STOP_LYRICS = False
            if _CURRENT_LYRICS:
                _LYRICS_THREAD = threading.Thread(target=display_lyrics_thread)
                _LYRICS_THREAD.daemon = True
                _LYRICS_THREAD.start()
                logger.info("歌词显示线程已启动")

            return f"开始播放: {song_name}，文件路径: {music_path}"

        except Exception as e:
            logger.error(f"播放失败: {str(e)}")
            return f"播放失败: {str(e)}"

@mcp.tool()
def pauseMusic() -> str:
    """
    暂停当前播放的音乐
    Returns:
        str: 操作结果
    """
    global _IS_PLAYING

    with _LOCK:
        try:
            # 检查pygame是否初始化
            if not _PLAYER_INITIALIZED:
                return "错误：播放器未初始化"

            # 检查是否有音乐在播放
            if not pygame.mixer.music.get_busy():
                return "错误：当前没有音乐在播放"

            # 暂停音乐
            if _IS_PLAYING:
                pygame.mixer.music.pause()
                _IS_PLAYING = False
                return f"已暂停播放: {_CURRENT_SONG}"
            else:
                # 如果已经暂停，则恢复播放
                pygame.mixer.music.unpause()
                _IS_PLAYING = True
                return f"已恢复播放: {_CURRENT_SONG}"

        except Exception as e:
            logger.error(f"暂停操作失败: {str(e)}")
            return f"暂停操作失败: {str(e)}"

@mcp.tool()
def stopMusic() -> str:
    """
    停止当前播放的音乐
    Returns:
        str: 操作结果
    """
    global _CURRENT_SONG, _IS_PLAYING, _STOP_LYRICS

    with _LOCK:
        try:
            # 检查pygame是否初始化
            if not _PLAYER_INITIALIZED:
                return "错误：播放器未初始化"

            # 检查是否有音乐在播放
            if not pygame.mixer.music.get_busy() and not _IS_PLAYING:
                return "错误：当前没有音乐在播放"

            # 停止音乐和歌词显示
            pygame.mixer.music.stop()
            _STOP_LYRICS = True  # 停止歌词显示线程
            song_name = _CURRENT_SONG
            _CURRENT_SONG = None
            _IS_PLAYING = False

            return f"已停止播放: {song_name}"

        except Exception as e:
            logger.error(f"停止操作失败: {str(e)}")
            return f"停止操作失败: {str(e)}"

@mcp.tool()
def showLyrics() -> str:
    """
    显示当前歌曲的歌词列表
    Returns:
        str: 歌词内容或错误信息
    """
    global _CURRENT_LYRICS, _CURRENT_SONG

    if not _CURRENT_SONG:
        return "错误：当前没有播放歌曲"

    if not _CURRENT_LYRICS:
        return f"当前歌曲 '{_CURRENT_SONG}' 没有歌词数据"

    lyrics_text = f"\n🎵 {_CURRENT_SONG} - 歌词 🎵\n"
    lyrics_text += "="*50 + "\n"

    for timestamp, lyric in _CURRENT_LYRICS:
        minutes = int(timestamp // 60)
        seconds = timestamp % 60
        lyrics_text += f"[{minutes:02d}:{seconds:05.2f}] {lyric}\n"

    lyrics_text += "="*50

    # 使用stderr输出，确保在MCP环境中可见
    sys.stderr.write(lyrics_text + "\n")
    sys.stderr.flush()

    return f"已显示歌曲 '{_CURRENT_SONG}' 的完整歌词，共{len(_CURRENT_LYRICS)}行"

@mcp.tool()
def testLyricsDisplay() -> str:
    """
    测试歌词显示功能
    Returns:
        str: 测试结果
    """
    global _CURRENT_LYRICS

    # 创建测试歌词数据
    test_lyrics = [
        (0.0, "测试歌词第一行"),
        (2.0, "测试歌词第二行"),
        (4.0, "测试歌词第三行"),
        (6.0, "测试歌词第四行")
    ]

    _CURRENT_LYRICS = test_lyrics
    logger.info("开始测试歌词显示...")

    # 立即显示所有测试歌词
    sys.stderr.write("\n" + "="*50 + "\n")
    sys.stderr.write("🎵 测试歌词显示 🎵\n")
    sys.stderr.write("="*50 + "\n")
    sys.stderr.flush()

    for timestamp, lyric in test_lyrics:
        sys.stderr.write(f"🎤 [{timestamp:.1f}s] {lyric}\n")
        sys.stderr.flush()
        time.sleep(0.5)  # 每0.5秒显示一行

    sys.stderr.write("="*50 + "\n")
    sys.stderr.write("🎵 测试结束 🎵\n")
    sys.stderr.write("="*50 + "\n\n")
    sys.stderr.flush()

    return "歌词显示测试完成"

@mcp.tool()
def testYaohudApi(song_name: str = "五道口") -> str:
    """
    测试yaohud API的响应
    Args:
        song_name: 要测试的歌曲名，默认为"五道口"
    Returns:
        str: 测试结果
    """
    try:
        logger.info(f"测试yaohud API搜索: {song_name}")
        params = {'key': _API_KEY, 'msg': song_name, 'n': '1'}
        resp = requests.post(_API_URL, params=params, timeout=10)
        resp.raise_for_status()

        response_data = resp.json()
        logger.info(f"API原始响应: {response_data}")

        if 'data' in response_data:
            music_data = response_data['data']
            music_url = music_data.get('musicurl', '')
            lyrics_data = music_data.get('lrctxt', {}).get('data', '')

            result = f"API测试成功！\n"
            result += f"音乐链接: {'有效' if music_url and music_url != 'null' else '无效'}\n"
            result += f"歌词数据: {'有' if lyrics_data else '无'}\n"

            if music_url and music_url != 'null':
                result += f"链接预览: {music_url[:100]}...\n"

            if lyrics_data:
                result += f"歌词预览: {lyrics_data[:100]}..."

            return result
        else:
            return f"API响应格式异常: {response_data}"

    except Exception as e:
        return f"API测试失败: {str(e)}"

@mcp.tool()
def getMusicStatus() -> str:
    """
    获取当前音乐播放状态
    Returns:
        str: 当前播放状态信息
    """
    global _CURRENT_SONG, _IS_PLAYING, _PLAYER_INITIALIZED

    if not _PLAYER_INITIALIZED:
        return "播放器状态：未初始化"

    if not _CURRENT_SONG:
        return "播放器状态：空闲，没有加载歌曲"

    if pygame.mixer.music.get_busy():
        status = "正在播放" if _IS_PLAYING else "已暂停"
    else:
        status = "已停止"

    lyrics_info = f"，歌词：{'有' if _CURRENT_LYRICS else '无'} ({len(_CURRENT_LYRICS)}行)"

    return f"播放器状态：{status}，当前歌曲：{_CURRENT_SONG}{lyrics_info}"


def main() -> None:
    mcp.run(transport="stdio")  # MCP标准输入输出模式
