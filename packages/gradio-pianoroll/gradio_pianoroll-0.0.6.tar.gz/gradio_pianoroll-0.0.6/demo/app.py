import gradio as gr
import numpy as np
import io
import base64
import wave
import tempfile
import os
from gradio_pianoroll import PianoRoll

# F0 분석을 위한 추가 import
try:
    import librosa
    LIBROSA_AVAILABLE = True
    print("✅ librosa 사용 가능")
except ImportError:
    LIBROSA_AVAILABLE = False
    print("⚠️ librosa가 설치되지 않음. F0 분석 기능이 제한됩니다.")

# 신디사이저 설정
SAMPLE_RATE = 44100
MAX_DURATION = 10.0  # 최대 10초

# 사용자 정의 phoneme 매핑 (전역 상태)
user_phoneme_map = {}

def initialize_phoneme_map():
    """기본 한국어 phoneme 매핑으로 초기화"""
    global user_phoneme_map
    user_phoneme_map = {
        '가': 'g a',
        '나': 'n a',
        '다': 'd a',
        '라': 'l aa',
        '마': 'm a',
        '바': 'b a',
        '사': 's a',
        '아': 'aa',
        '자': 'j a',
        '차': 'ch a',
        '카': 'k a',
        '타': 't a',
        '파': 'p a',
        '하': 'h a',
        '도': 'd o',
        '레': 'l e',
        '미': 'm i',
        '파': 'p aa',
        '솔': 's o l',
        '라': 'l aa',
        '시': 's i',
        '안녕': 'aa n ny eo ng',
        '하세요': 'h a s e y o',
        '노래': 'n o l ae',
        '사랑': 's a l a ng',
        '행복': 'h ae ng b o k',
        '음악': 'eu m a k',
        '피아노': 'p i a n o'
    }

# 프로그램 시작 시 phoneme 매핑 초기화
initialize_phoneme_map()

def get_phoneme_mapping_list():
    """현재 phoneme 매핑 리스트 반환 (UI 표시용)"""
    global user_phoneme_map
    return [{"lyric": k, "phoneme": v} for k, v in user_phoneme_map.items()]

def get_phoneme_mapping_for_dataframe():
    """Dataframe용 phoneme 매핑 리스트 반환"""
    global user_phoneme_map
    return [[k, v] for k, v in user_phoneme_map.items()]

def add_phoneme_mapping(lyric: str, phoneme: str):
    """새로운 phoneme 매핑 추가"""
    global user_phoneme_map
    user_phoneme_map[lyric.strip()] = phoneme.strip()
    return get_phoneme_mapping_for_dataframe(), f"'{lyric}' → '{phoneme}' 매핑이 추가되었습니다."

def update_phoneme_mapping(old_lyric: str, new_lyric: str, new_phoneme: str):
    """기존 phoneme 매핑 수정"""
    global user_phoneme_map

    # 기존 매핑 삭제
    if old_lyric in user_phoneme_map:
        del user_phoneme_map[old_lyric]

    # 새 매핑 추가
    user_phoneme_map[new_lyric.strip()] = new_phoneme.strip()
    return get_phoneme_mapping_for_dataframe(), f"매핑이 '{new_lyric}' → '{new_phoneme}'로 수정되었습니다."

def delete_phoneme_mapping(lyric: str):
    """phoneme 매핑 삭제"""
    global user_phoneme_map
    if lyric in user_phoneme_map:
        del user_phoneme_map[lyric]
        return get_phoneme_mapping_for_dataframe(), f"'{lyric}' 매핑이 삭제되었습니다."
    else:
        return get_phoneme_mapping_for_dataframe(), f"'{lyric}' 매핑을 찾을 수 없습니다."

def reset_phoneme_mapping():
    """phoneme 매핑을 기본값으로 리셋"""
    initialize_phoneme_map()
    return get_phoneme_mapping_for_dataframe(), "Phoneme 매핑이 기본값으로 리셋되었습니다."

def midi_to_frequency(midi_note):
    """MIDI 노트 번호를 주파수로 변환 (A4 = 440Hz)"""
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

def create_adsr_envelope(attack, decay, sustain, release, duration, sample_rate):
    """ADSR 엔벨로프를 생성"""
    total_samples = int(duration * sample_rate)
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)
    sustain_samples = total_samples - attack_samples - decay_samples - release_samples

    # 지속 구간이 음수가 되지 않도록 조정
    if sustain_samples < 0:
        sustain_samples = 0
        total_samples = attack_samples + decay_samples + release_samples

    envelope = np.zeros(total_samples)

    # Attack phase
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

    # Decay phase
    if decay_samples > 0:
        start_idx = attack_samples
        end_idx = attack_samples + decay_samples
        envelope[start_idx:end_idx] = np.linspace(1, sustain, decay_samples)

    # Sustain phase
    if sustain_samples > 0:
        start_idx = attack_samples + decay_samples
        end_idx = start_idx + sustain_samples
        envelope[start_idx:end_idx] = sustain

    # Release phase
    if release_samples > 0:
        start_idx = attack_samples + decay_samples + sustain_samples
        envelope[start_idx:] = np.linspace(sustain, 0, release_samples)

    return envelope

def generate_sine_wave(frequency, duration, sample_rate):
    """사인파 생성"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    return np.sin(2 * np.pi * frequency * t)

def generate_sawtooth_wave(frequency, duration, sample_rate):
    """톱니파 생성"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    # 2 * (t * frequency - np.floor(0.5 + t * frequency))
    return 2 * (t * frequency % 1) - 1

def generate_square_wave(frequency, duration, sample_rate):
    """사각파 생성"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    return np.sign(np.sin(2 * np.pi * frequency * t))

def generate_triangle_wave(frequency, duration, sample_rate):
    """삼각파 생성"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    return 2 * np.abs(2 * (t * frequency % 1) - 1) - 1

def generate_harmonic_wave(frequency, duration, sample_rate, harmonics=5):
    """하모닉을 포함한 복합 파형 생성"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    wave = np.zeros_like(t)

    # 기본 주파수
    wave += np.sin(2 * np.pi * frequency * t)

    # 하모닉 추가 (각 하모닉의 진폭은 1/n로 감소)
    for n in range(2, harmonics + 1):
        amplitude = 1.0 / n
        wave += amplitude * np.sin(2 * np.pi * frequency * n * t)

    # 정규화
    wave = wave / np.max(np.abs(wave))
    return wave

def generate_fm_wave(frequency, duration, sample_rate, mod_freq=5.0, mod_depth=2.0):
    """FM 합성 파형 생성"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)

    # Modulator
    modulator = mod_depth * np.sin(2 * np.pi * mod_freq * t)

    # Carrier with frequency modulation
    carrier = np.sin(2 * np.pi * frequency * t + modulator)

    return carrier

def generate_complex_wave(frequency, duration, sample_rate, wave_type='complex'):
    """복합적인 파형 생성 (여러 기법 조합)"""
    if wave_type == 'sine':
        return generate_sine_wave(frequency, duration, sample_rate)
    elif wave_type == 'sawtooth':
        return generate_sawtooth_wave(frequency, duration, sample_rate)
    elif wave_type == 'square':
        return generate_square_wave(frequency, duration, sample_rate)
    elif wave_type == 'triangle':
        return generate_triangle_wave(frequency, duration, sample_rate)
    elif wave_type == 'harmonic':
        return generate_harmonic_wave(frequency, duration, sample_rate, harmonics=7)
    elif wave_type == 'fm':
        return generate_fm_wave(frequency, duration, sample_rate, mod_freq=frequency * 0.1, mod_depth=3.0)
    else:  # 'complex' - 여러 파형 조합
        # 기본 sawtooth + 하모닉 + 약간의 FM
        base = generate_sawtooth_wave(frequency, duration, sample_rate) * 0.6
        harmonic = generate_harmonic_wave(frequency, duration, sample_rate, harmonics=4) * 0.3
        fm = generate_fm_wave(frequency, duration, sample_rate, mod_freq=frequency * 0.05, mod_depth=1.0) * 0.1

        return base + harmonic + fm

def synthesize_audio(piano_roll_data, attack=0.01, decay=0.1, sustain=0.7, release=0.3, wave_type='complex'):
    """피아노롤 데이터로부터 오디오를 합성"""
    if not piano_roll_data or 'notes' not in piano_roll_data or not piano_roll_data['notes']:
        return None

    notes = piano_roll_data['notes']
    tempo = piano_roll_data.get('tempo', 120)
    pixels_per_beat = piano_roll_data.get('pixelsPerBeat', 80)

    # 전체 길이 계산 (마지막 노트의 끝까지)
    max_end_time = 0
    for note in notes:
        # 픽셀을 초로 변환 (템포와 픽셀당 비트 수 고려)
        start_seconds = (note['start'] / pixels_per_beat) * (60.0 / tempo)
        duration_seconds = (note['duration'] / pixels_per_beat) * (60.0 / tempo)
        end_time = start_seconds + duration_seconds
        max_end_time = max(max_end_time, end_time)

    # 최대 길이 제한
    total_duration = min(max_end_time + 1.0, MAX_DURATION)  # 1초 여유 추가
    total_samples = int(total_duration * SAMPLE_RATE)

    # 최종 오디오 버퍼
    audio_buffer = np.zeros(total_samples)

    # 각 노트 처리
    for i, note in enumerate(notes):
        try:
            # 노트 속성
            pitch = note['pitch']
            velocity = note.get('velocity', 100)

            # 시간 계산
            start_seconds = (note['start'] / pixels_per_beat) * (60.0 / tempo)
            duration_seconds = (note['duration'] / pixels_per_beat) * (60.0 / tempo)

            # 범위 체크
            if start_seconds >= total_duration:
                continue

            # 지속 시간이 전체 길이를 초과하지 않도록 조정
            if start_seconds + duration_seconds > total_duration:
                duration_seconds = total_duration - start_seconds

            if duration_seconds <= 0:
                continue

            # 주파수 계산
            frequency = midi_to_frequency(pitch)

            # 볼륨 계산 (velocity를 0-1로 정규화)
            volume = velocity / 127.0

            # 모든 노트에 동일한 파형 타입 사용 (일관성 유지)
            # 복합 파형 생성
            base_wave = generate_complex_wave(frequency, duration_seconds, SAMPLE_RATE, wave_type)

            # 추가 효과: 비브라토 (주파수 변조)
            t = np.linspace(0, duration_seconds, len(base_wave), False)
            vibrato_freq = 4.5  # 4.5Hz 비브라토
            vibrato_depth = 0.02  # 2% 주파수 변조
            vibrato = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_freq * t)

            # 비브라토를 파형에 적용 (간단한 근사)
            vibrato_wave = base_wave * vibrato

            # 추가 효과: 트레몰로 (진폭 변조)
            tremolo_freq = 3.0  # 3Hz 트레몰로
            tremolo_depth = 0.1  # 10% 진폭 변조
            tremolo = 1 + tremolo_depth * np.sin(2 * np.pi * tremolo_freq * t)

            # 트레몰로 적용
            final_wave = vibrato_wave * tremolo

            # ADSR 엔벨로프 적용
            envelope = create_adsr_envelope(attack, decay, sustain, release, duration_seconds, SAMPLE_RATE)

            # 엔벨로프와 파형 길이 맞춤
            min_length = min(len(final_wave), len(envelope))
            note_audio = final_wave[:min_length] * envelope[:min_length] * volume * 0.25  # 볼륨 조절

            # 오디오 버퍼에 추가
            start_sample = int(start_seconds * SAMPLE_RATE)
            end_sample = start_sample + len(note_audio)

            # 버퍼 범위 내에서만 추가
            if start_sample < total_samples:
                end_sample = min(end_sample, total_samples)
                audio_length = end_sample - start_sample
                if audio_length > 0:
                    audio_buffer[start_sample:end_sample] += note_audio[:audio_length]

        except Exception as e:
            print(f"노트 처리 중 오류: {e}")
            continue

    # 클리핑 방지 (normalize)
    max_amplitude = np.max(np.abs(audio_buffer))
    if max_amplitude > 0:
        audio_buffer = audio_buffer / max_amplitude * 0.9  # 90%로 제한

    return audio_buffer

def audio_to_base64_wav(audio_data, sample_rate):
    """오디오 데이터를 base64 인코딩된 WAV로 변환"""
    if audio_data is None or len(audio_data) == 0:
        return None

    # 16비트 PCM으로 변환
    audio_16bit = (audio_data * 32767).astype(np.int16)

    # WAV 파일을 메모리에 생성
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # 모노
        wav_file.setsampwidth(2)  # 16비트
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_16bit.tobytes())

    # base64 인코딩
    buffer.seek(0)
    wav_data = buffer.read()
    base64_data = base64.b64encode(wav_data).decode('utf-8')

    return f"data:audio/wav;base64,{base64_data}"

def calculate_waveform_data(audio_data, pixels_per_beat, tempo, target_width=1000):
    """오디오 데이터로부터 웨이브폼 시각화 데이터를 계산"""
    if audio_data is None or len(audio_data) == 0:
        return None

    # 오디오 총 길이 (초)
    audio_duration = len(audio_data) / SAMPLE_RATE

    # 총 픽셀 길이 계산 (템포와 픽셀당 비트 기반)
    total_pixels = (tempo / 60) * pixels_per_beat * audio_duration

    # 각 픽셀당 샘플 수 계산
    samples_per_pixel = len(audio_data) / total_pixels

    waveform_points = []

    # 각 픽셀에 대해 min/max 값 계산
    for pixel in range(int(total_pixels)):
        start_sample = int(pixel * samples_per_pixel)
        end_sample = int((pixel + 1) * samples_per_pixel)
        end_sample = min(end_sample, len(audio_data))

        if start_sample >= len(audio_data):
            break

        if start_sample < end_sample:
            # 해당 픽셀 범위의 오디오 데이터
            pixel_data = audio_data[start_sample:end_sample]

            # min, max 값 계산
            min_val = float(np.min(pixel_data))
            max_val = float(np.max(pixel_data))

            # 시간 정보 (픽셀 위치)
            time_position = pixel

            waveform_points.append({
                'x': time_position,
                'min': min_val,
                'max': max_val
            })

    return waveform_points

def convert_basic(piano_roll):
    """기본 변환 함수 (첫 번째 탭용)"""
    print("=== Basic Convert function called ===")
    print("Received piano_roll:")
    print(piano_roll)
    print("Type:", type(piano_roll))
    return piano_roll

def synthesize_and_play(piano_roll, attack, decay, sustain, release, wave_type='complex'):
    """신디사이저로 오디오를 생성하고 피아노롤에 전달"""
    print("=== Synthesize function called ===")
    print("Piano roll data:", piano_roll)
    print(f"ADSR: A={attack}, D={decay}, S={sustain}, R={release}")
    print(f"Wave Type: {wave_type}")

    # 오디오 합성
    audio_data = synthesize_audio(piano_roll, attack, decay, sustain, release, wave_type)

    if audio_data is None:
        print("오디오 생성 실패")
        return piano_roll, "오디오 생성 실패", None

    # base64로 변환 (피아노롤용)
    audio_base64 = audio_to_base64_wav(audio_data, SAMPLE_RATE)

    # gradio Audio 컴포넌트용 WAV 파일 생성
    gradio_audio_path = create_temp_wav_file(audio_data, SAMPLE_RATE)

    # 피아노롤 데이터에 오디오 추가
    updated_piano_roll = piano_roll.copy() if piano_roll else {}
    updated_piano_roll['audio_data'] = audio_base64
    updated_piano_roll['use_backend_audio'] = True

    print(f"🔊 [synthesize_and_play] Setting backend audio data:")
    print(f"   - audio_data length: {len(audio_base64) if audio_base64 else 0}")
    print(f"   - use_backend_audio: {updated_piano_roll['use_backend_audio']}")
    print(f"   - audio_base64 preview: {audio_base64[:50] + '...' if audio_base64 else 'None'}")

    # 웨이브폼 데이터 계산
    pixels_per_beat = updated_piano_roll.get('pixelsPerBeat', 80)
    tempo = updated_piano_roll.get('tempo', 120)
    waveform_data = calculate_waveform_data(audio_data, pixels_per_beat, tempo)

    # 곡선 데이터 예시 (피치 곡선 + 웨이브폼 데이터)
    curve_data = {}

    # 웨이브폼 데이터 추가
    if waveform_data:
        curve_data['waveform_data'] = waveform_data
        print(f"웨이브폼 데이터 생성: {len(waveform_data)} 포인트")

    # 피치 곡선 데이터 (기존)
    if 'notes' in updated_piano_roll and updated_piano_roll['notes']:
        pitch_curve = []
        for note in updated_piano_roll['notes']:
            # 간단한 예시: 노트의 피치를 기반으로 곡선 생성
            base_pitch = note['pitch']
            # 약간의 비브라토 효과
            curve_points = [base_pitch + 0.5 * np.sin(i * 0.5) for i in range(10)]
            pitch_curve.extend(curve_points)

        curve_data['pitch_curve'] = pitch_curve[:100]  # 최대 100개 포인트로 제한

    updated_piano_roll['curve_data'] = curve_data

    # 세그먼트 데이터 예시 (발음 타이밍)
    if 'notes' in updated_piano_roll and updated_piano_roll['notes']:
        segment_data = []

        for i, note in enumerate(updated_piano_roll['notes']):
            start_seconds = (note['start'] / pixels_per_beat) * (60.0 / tempo)
            duration_seconds = (note['duration'] / pixels_per_beat) * (60.0 / tempo)

            segment_data.append({
                'start': start_seconds,
                'end': start_seconds + duration_seconds,
                'type': 'note',
                'value': note.get('lyric', f"Note_{i+1}"),
                'confidence': 0.95
            })

        updated_piano_roll['segment_data'] = segment_data

    print(f"오디오 생성 완료: {len(audio_data)} 샘플")
    if waveform_data:
        print(f"웨이브폼 포인트: {len(waveform_data)}개")

    status_message = f"오디오 생성 완료 ({wave_type} 파형): {len(audio_data)} 샘플, 길이: {len(audio_data)/SAMPLE_RATE:.2f}초"

    return updated_piano_roll, status_message, gradio_audio_path

def create_temp_wav_file(audio_data, sample_rate):
    """gradio Audio 컴포넌트용 임시 WAV 파일 생성"""
    if audio_data is None or len(audio_data) == 0:
        return None

    try:
        # 16비트 PCM으로 변환
        audio_16bit = (audio_data * 32767).astype(np.int16)

        # 임시 파일 생성
        temp_fd, temp_path = tempfile.mkstemp(suffix='.wav')

        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # 모노
            wav_file.setsampwidth(2)  # 16비트
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_16bit.tobytes())

        # 파일 디스크립터 닫기
        os.close(temp_fd)

        return temp_path
    except Exception as e:
        print(f"임시 WAV 파일 생성 오류: {e}")
        return None

def clear_and_regenerate_waveform(piano_roll, attack, decay, sustain, release, wave_type='complex'):
    """웨이브폼을 지우고 다시 생성"""
    print("=== Clear and Regenerate Waveform ===")

    # 먼저 웨이브폼 데이터를 지움
    cleared_piano_roll = piano_roll.copy() if piano_roll else {}
    cleared_piano_roll['curve_data'] = {}  # 곡선 데이터 초기화
    cleared_piano_roll['audio_data'] = None  # 오디오 데이터 초기화
    cleared_piano_roll['use_backend_audio'] = False  # 백엔드 오디오 비활성화

    # 잠시 대기를 위한 메시지
    yield cleared_piano_roll, "웨이브폼을 지우는 중...", None

    # 그 다음 새로운 웨이브폼 생성
    result_piano_roll, status_message, gradio_audio_path = synthesize_and_play(piano_roll, attack, decay, sustain, release, wave_type)

    yield result_piano_roll, f"재생성 완료! {status_message}", gradio_audio_path

# G2P (Grapheme-to-Phoneme) 함수 (사용자 정의 매핑 사용)
def mock_g2p(text: str) -> str:
    """
    사용자 정의 매핑을 사용하는 한국어 G2P 함수
    """
    global user_phoneme_map

    # 텍스트를 소문자로 변환하고 공백 제거
    text = text.strip()

    # 사용자 정의 매핑에서 찾기
    if text in user_phoneme_map:
        return user_phoneme_map[text]

    # 매핑에 없으면 글자별로 처리
    result = []
    for char in text:
        if char in user_phoneme_map:
            result.append(user_phoneme_map[char])
        else:
            # 알 수 없는 글자는 그대로 반환
            result.append(char)

    return ' '.join(result)

def process_lyric_input(piano_roll, lyric_data):
    """
    가사 입력 이벤트를 처리하고 G2P를 실행하여 phoneme을 생성
    """
    print("=== G2P Processing ===")
    print("Piano roll data:", piano_roll)
    print("Lyric data:", lyric_data)

    if not piano_roll or not lyric_data:
        return piano_roll, "가사 데이터가 없습니다."

    # 새로운 가사에 대해 G2P 실행
    new_lyric = lyric_data.get('newLyric', '')
    if new_lyric:
        # G2P 실행 (모킹 함수 사용)
        phoneme = mock_g2p(new_lyric)
        print(f"G2P 결과: '{new_lyric}' -> '{phoneme}'")

        # 해당 노트의 phoneme 업데이트
        note_id = lyric_data.get('noteId')
        if note_id and 'notes' in piano_roll:
            notes = piano_roll['notes'].copy()
            for note in notes:
                if note.get('id') == note_id:
                    note['phoneme'] = phoneme
                    print(f"노트 {note_id}의 phoneme 업데이트: {phoneme}")
                    break

            # 업데이트된 피아노롤 데이터 반환
            updated_piano_roll = piano_roll.copy()
            updated_piano_roll['notes'] = notes

            return updated_piano_roll, f"G2P 완료: '{new_lyric}' -> [{phoneme}]"

    return piano_roll, "G2P 처리 완료"

def manual_phoneme_update(piano_roll, note_index, phoneme_text):
    """
    수동으로 특정 노트의 phoneme을 업데이트
    """
    print(f"=== Manual Phoneme Update ===")
    print(f"Note index: {note_index}, Phoneme: '{phoneme_text}'")

    if not piano_roll or 'notes' not in piano_roll:
        return piano_roll, "피아노롤 데이터가 없습니다."

    notes = piano_roll['notes'].copy()

    if 0 <= note_index < len(notes):
        notes[note_index]['phoneme'] = phoneme_text

        updated_piano_roll = piano_roll.copy()
        updated_piano_roll['notes'] = notes

        lyric = notes[note_index].get('lyric', '?')
        return updated_piano_roll, f"노트 {note_index + 1} ('{lyric}')의 phoneme을 '{phoneme_text}'로 설정했습니다."
    else:
        return piano_roll, f"잘못된 노트 인덱스: {note_index}"

def clear_all_phonemes(piano_roll):
    """
    모든 노트의 phoneme을 지우기
    """
    print("=== Clear All Phonemes ===")

    if not piano_roll or 'notes' not in piano_roll:
        return piano_roll, "피아노롤 데이터가 없습니다."

    notes = piano_roll['notes'].copy()

    for note in notes:
        note['phoneme'] = None

    updated_piano_roll = piano_roll.copy()
    updated_piano_roll['notes'] = notes

    return updated_piano_roll, "모든 phoneme이 지워졌습니다."

def auto_generate_all_phonemes(piano_roll):
    """
    모든 노트의 가사에 대해 자동으로 phoneme 생성
    """
    print("=== Auto Generate All Phonemes ===")

    if not piano_roll or 'notes' not in piano_roll:
        return piano_roll, "피아노롤 데이터가 없습니다."

    notes = piano_roll['notes'].copy()

    updated_count = 0
    for note in notes:
        lyric = note.get('lyric')
        if lyric:
            phoneme = mock_g2p(lyric)
            note['phoneme'] = phoneme
            updated_count += 1
            print(f"자동 생성: '{lyric}' -> '{phoneme}'")

    updated_piano_roll = piano_roll.copy()
    updated_piano_roll['notes'] = notes

    return updated_piano_roll, f"{updated_count}개 노트의 phoneme이 자동 생성되었습니다."

# F0 및 오디오 특성 분석 함수들
def extract_f0_from_audio(audio_file_path, f0_method="pyin"):
    """
    오디오 파일에서 F0(기본 주파수)를 추출합니다.
    """
    if not LIBROSA_AVAILABLE:
        return None, "librosa가 설치되지 않아 F0 분석을 수행할 수 없습니다."

    try:
        print(f"🎵 F0 추출 시작: {audio_file_path}")

        # 오디오 로드
        y, sr = librosa.load(audio_file_path, sr=None)
        print(f"   - 샘플레이트: {sr}Hz")
        print(f"   - 길이: {len(y)/sr:.2f}초")

        # F0 추출 방법 선택
        if f0_method == "pyin":
            # PYIN 알고리즘 사용 (더 정확하지만 느림)
            f0, voiced_flag, voiced_probs = librosa.pyin(
                y,
                sr=sr,
                fmin=librosa.note_to_hz('C2'),  # 약 65Hz
                fmax=librosa.note_to_hz('C7')   # 약 2093Hz
            )
        else:
            # 기본 피치 추출
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            f0 = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                f0.append(pitch if pitch > 0 else np.nan)
            f0 = np.array(f0)

        # 시간 축 계산
        hop_length = 512  # librosa 기본값
        frame_times = librosa.frames_to_time(np.arange(len(f0)), sr=sr, hop_length=hop_length)

        # NaN 값 처리 및 스무딩
        valid_indices = ~np.isnan(f0)
        if np.sum(valid_indices) == 0:
            return None, "유효한 F0 값을 찾을 수 없습니다."

        # 유효한 F0 값만 사용
        valid_f0 = f0[valid_indices]
        valid_times = frame_times[valid_indices]

        print(f"   - 추출된 F0 포인트: {len(valid_f0)}개")
        print(f"   - F0 범위: {np.min(valid_f0):.1f}Hz ~ {np.max(valid_f0):.1f}Hz")

        # voiced/unvoiced 정보도 함께 반환
        result_data = {
            'times': frame_times,  # 전체 시간 축
            'f0_values': f0,  # 전체 F0 (NaN 포함)
            'valid_times': valid_times,  # 유효한 시간만
            'valid_f0_values': valid_f0,  # 유효한 F0만
            'sample_rate': sr,
            'duration': len(y) / sr,
            'hop_length': hop_length
        }

        # PYIN에서 voiced 정보 추가
        if f0_method == "pyin" and 'voiced_flag' in locals() and 'voiced_probs' in locals():
            result_data['voiced_flag'] = voiced_flag
            result_data['voiced_probs'] = voiced_probs
        else:
            # 다른 방법의 경우 F0 존재 여부로 voiced 추정
            voiced_flag = ~np.isnan(f0)
            voiced_probs = voiced_flag.astype(float)
            result_data['voiced_flag'] = voiced_flag
            result_data['voiced_probs'] = voiced_probs

        return result_data, "F0 추출 완료"

    except Exception as e:
        print(f"❌ F0 추출 오류: {e}")
        return None, f"F0 추출 오류: {str(e)}"

def extract_loudness_from_audio(audio_file_path):
    """
    오디오 파일에서 loudness(음량)를 추출합니다.
    """
    if not LIBROSA_AVAILABLE:
        return None, "librosa가 설치되지 않아 loudness 분석을 수행할 수 없습니다."

    try:
        print(f"🔊 Loudness 추출 시작: {audio_file_path}")

        # 오디오 로드
        y, sr = librosa.load(audio_file_path, sr=None)
        print(f"   - 샘플레이트: {sr}Hz")
        print(f"   - 길이: {len(y)/sr:.2f}초")

        # RMS 에너지 계산
        hop_length = 512
        rms_energy = librosa.feature.rms(y=y, hop_length=hop_length)[0]

        # 시간 축 계산
        frame_times = librosa.frames_to_time(np.arange(len(rms_energy)), sr=sr, hop_length=hop_length)

        # dB로 변환 (참조값: 최대 RMS)
        max_rms = np.max(rms_energy)
        if max_rms > 0:
            loudness_db = 20 * np.log10(rms_energy / max_rms)
            # -60dB 이하는 무음으로 처리
            loudness_db = np.maximum(loudness_db, -60)
        else:
            loudness_db = np.full_like(rms_energy, -60)

        # 0-1 범위로 정규화 (-60dB ~ 0dB -> 0 ~ 1)
        loudness_normalized = (loudness_db + 60) / 60

        print(f"   - 추출된 Loudness 포인트: {len(loudness_normalized)}개")
        print(f"   - RMS 범위: {np.min(rms_energy):.6f} ~ {np.max(rms_energy):.6f}")
        print(f"   - dB 범위: {np.min(loudness_db):.1f}dB ~ {np.max(loudness_db):.1f}dB")

        return {
            'times': frame_times,
            'rms_values': rms_energy,
            'loudness_db': loudness_db,
            'loudness_normalized': loudness_normalized,
            'sample_rate': sr,
            'duration': len(y) / sr,
            'hop_length': hop_length
        }, "Loudness 추출 완료"

    except Exception as e:
        print(f"❌ Loudness 추출 오류: {e}")
        return None, f"Loudness 추출 오류: {str(e)}"

def extract_voicing_from_audio(audio_file_path, f0_method="pyin"):
    """
    오디오 파일에서 voice/unvoice 정보를 추출합니다.
    """
    if not LIBROSA_AVAILABLE:
        return None, "librosa가 설치되지 않아 voice/unvoice 분석을 수행할 수 없습니다."

    try:
        print(f"🗣️ Voice/Unvoice 추출 시작: {audio_file_path}")

        # F0 분석에서 voiced 정보를 함께 얻음
        f0_data, f0_status = extract_f0_from_audio(audio_file_path, f0_method)

        if f0_data is None:
            return None, f"F0 분석 실패로 voice/unvoice 추출 불가: {f0_status}"

        # voiced 정보 추출
        times = f0_data['times']
        voiced_flag = f0_data['voiced_flag']
        voiced_probs = f0_data['voiced_probs']

        print(f"   - 추출된 Voice/Unvoice 포인트: {len(voiced_flag)}개")

        # voiced 구간 통계
        voiced_frames = np.sum(voiced_flag)
        voiced_ratio = voiced_frames / len(voiced_flag) if len(voiced_flag) > 0 else 0
        print(f"   - Voiced 구간: {voiced_frames}프레임 ({voiced_ratio:.1%})")
        print(f"   - Unvoiced 구간: {len(voiced_flag) - voiced_frames}프레임 ({1-voiced_ratio:.1%})")

        return {
            'times': times,
            'voiced_flag': voiced_flag,
            'voiced_probs': voiced_probs,
            'sample_rate': f0_data['sample_rate'],
            'duration': f0_data['duration'],
            'hop_length': f0_data['hop_length'],
            'voiced_ratio': voiced_ratio
        }, "Voice/Unvoice 추출 완료"

    except Exception as e:
        print(f"❌ Voice/Unvoice 추출 오류: {e}")
        return None, f"Voice/Unvoice 추출 오류: {str(e)}"

def extract_audio_features(audio_file_path, f0_method="pyin", include_f0=True, include_loudness=True, include_voicing=True):
    """
    오디오 파일에서 F0, loudness, voice/unvoice를 모두 추출합니다.
    """
    if not LIBROSA_AVAILABLE:
        return None, "librosa가 설치되지 않아 오디오 특성 분석을 수행할 수 없습니다."

    features = {}
    status_messages = []

    try:
        print(f"🎵 오디오 특성 분석 시작: {audio_file_path}")

        # F0 추출
        if include_f0:
            f0_data, f0_status = extract_f0_from_audio(audio_file_path, f0_method)
            if f0_data:
                features['f0'] = f0_data
                status_messages.append(f0_status)
            else:
                status_messages.append(f"F0 추출 실패: {f0_status}")

        # Loudness 추출
        if include_loudness:
            loudness_data, loudness_status = extract_loudness_from_audio(audio_file_path)
            if loudness_data:
                features['loudness'] = loudness_data
                status_messages.append(loudness_status)
            else:
                status_messages.append(f"Loudness 추출 실패: {loudness_status}")

        # Voice/Unvoice 추출
        if include_voicing:
            voicing_data, voicing_status = extract_voicing_from_audio(audio_file_path, f0_method)
            if voicing_data:
                features['voicing'] = voicing_data
                status_messages.append(voicing_status)
            else:
                status_messages.append(f"Voice/Unvoice 추출 실패: {voicing_status}")

        if features:
            # 공통 정보 추가
            if 'f0' in features:
                features['duration'] = features['f0']['duration']
                features['sample_rate'] = features['f0']['sample_rate']
            elif 'loudness' in features:
                features['duration'] = features['loudness']['duration']
                features['sample_rate'] = features['loudness']['sample_rate']
            elif 'voicing' in features:
                features['duration'] = features['voicing']['duration']
                features['sample_rate'] = features['voicing']['sample_rate']

            return features, " | ".join(status_messages)
        else:
            return None, "모든 특성 추출에 실패했습니다."

    except Exception as e:
        print(f"❌ 오디오 특성 분석 오류: {e}")
        return None, f"오디오 특성 분석 오류: {str(e)}"

def create_f0_line_data(f0_data, tempo=120, pixelsPerBeat=80):
    """
    F0 데이터를 LineLayer용 line_data 형식으로 변환합니다.
    F0 곡선이 피아노롤 그리드의 정확한 피치 위치에 표시되도록 변환합니다.
    """
    if not f0_data:
        return None

    try:
        times = f0_data['times']
        f0_values = f0_data['f0_values']

        # 피아노롤 상수들 (GridComponent와 동일)
        NOTE_HEIGHT = 20
        TOTAL_NOTES = 128

        def hz_to_midi(frequency):
            """주파수(Hz)를 MIDI 노트 번호로 변환"""
            if frequency <= 0:
                return 0
            return 69 + 12 * np.log2(frequency / 440.0)

        def midi_to_y_coordinate(midi_note):
            """MIDI 노트 번호를 피아노롤 Y 좌표로 변환 (GridComponent와 동일한 방식)"""
            return (TOTAL_NOTES - 1 - midi_note) * NOTE_HEIGHT + NOTE_HEIGHT/2

        # 데이터 포인트 생성 (피아노롤 좌표계 사용)
        data_points = []
        valid_f0_values = []

        for time, f0 in zip(times, f0_values):
            if not np.isnan(f0) and f0 > 0:
                # Hz를 MIDI로 변환
                midi_note = hz_to_midi(f0)

                # MIDI 범위 체크 (0-127)
                if 0 <= midi_note <= 127:
                    # 시간(초)을 픽셀 X 좌표로 변환
                    x_pixel = time * (tempo / 60) * pixelsPerBeat

                    # MIDI를 피아노롤 Y 좌표로 변환
                    y_pixel = midi_to_y_coordinate(midi_note)

                    data_points.append({
                        "x": float(x_pixel),
                        "y": float(y_pixel)
                    })
                    valid_f0_values.append(f0)

        if not data_points:
            print("⚠️ 유효한 F0 데이터 포인트가 없습니다.")
            return None

        # F0 값 범위 정보 (표시용)
        min_f0 = float(np.min(valid_f0_values))
        max_f0 = float(np.max(valid_f0_values))
        min_midi = hz_to_midi(min_f0)
        max_midi = hz_to_midi(max_f0)

        # Y 범위를 전체 피아노롤 범위로 설정
        y_min = 0
        y_max = TOTAL_NOTES * NOTE_HEIGHT

        line_data = {
            "f0_curve": {
                "color": "#FF6B6B",  # 빨간색
                "lineWidth": 3,
                "yMin": y_min,
                "yMax": y_max,
                "position": "overlay",  # 그리드 위에 오버레이
                "renderMode": "piano_grid",  # F0 전용 렌더링 모드
                "visible": True,
                "opacity": 0.8,
                "data": data_points,
                # 메타데이터
                "dataType": "f0",
                "unit": "Hz",
                "originalRange": {
                    "minHz": min_f0,
                    "maxHz": max_f0,
                    "minMidi": min_midi,
                    "maxMidi": max_midi
                }
            }
        }

        print(f"📊 F0 LineData 생성 완료: {len(data_points)}개 포인트")
        print(f"   - F0 범위: {min_f0:.1f}Hz ~ {max_f0:.1f}Hz")
        print(f"   - MIDI 범위: {min_midi:.1f} ~ {max_midi:.1f}")
        print(f"   - 렌더링 모드: 피아노롤 그리드 정렬")

        return line_data

    except Exception as e:
        print(f"❌ F0 LineData 생성 오류: {e}")
        return None

def create_loudness_line_data(loudness_data, tempo=120, pixelsPerBeat=80, y_min=None, y_max=None, use_db=True):
    """
    Loudness 데이터를 LineLayer용 line_data 형식으로 변환합니다.
    독립적인 Y축 범위를 가지며 피아노롤 그리드와 별도로 표시됩니다.
    """
    if not loudness_data:
        return None

    try:
        times = loudness_data['times']

        # 사용할 loudness 값 선택 (dB 또는 정규화된 값)
        if use_db:
            values = loudness_data['loudness_db']
            unit = "dB"
            default_y_min = -60
            default_y_max = 0
        else:
            values = loudness_data['loudness_normalized']
            unit = "normalized"
            default_y_min = 0
            default_y_max = 1

        # Y축 범위 설정
        actual_y_min = y_min if y_min is not None else default_y_min
        actual_y_max = y_max if y_max is not None else default_y_max
        y_range = actual_y_max - actual_y_min

        # 데이터 포인트 생성
        data_points = []
        for time, value in zip(times, values):
            if not np.isnan(value):
                # 시간(초)을 픽셀 X 좌표로 변환
                x_pixel = time * (tempo / 60) * pixelsPerBeat

                # Loudness 값을 0-2560 픽셀 범위로 변환 (전체 grid canvas 높이 사용)
                normalized_value = (value - actual_y_min) / y_range
                y_pixel = normalized_value * 2560  # 0-2560 픽셀 범위 (128개 노트 * 20픽셀 높이)

                data_points.append({
                    "x": float(x_pixel),
                    "y": float(max(0, min(2560, y_pixel)))  # 범위 제한
                })

        if not data_points:
            print("⚠️ 유효한 Loudness 데이터 포인트가 없습니다.")
            return None

        # 실제 값 범위
        min_value = float(np.min(values))
        max_value = float(np.max(values))

        line_data = {
            "loudness_curve": {
                "color": "#4ECDC4",  # 청록색
                "lineWidth": 2,
                "yMin": 0,
                "yMax": 2560,  # 전체 grid canvas 높이 (128개 노트 * 20픽셀)
                "position": "overlay",  # 전체 영역에 오버레이로 표시
                "renderMode": "independent_range",  # 독립적인 Y축 범위
                "visible": True,
                "opacity": 0.6,
                "data": data_points,
                # 메타데이터
                "dataType": "loudness",
                "unit": unit,
                "originalRange": {
                    "min": min_value,
                    "max": max_value,
                    "y_min": actual_y_min,
                    "y_max": actual_y_max
                }
            }
        }

        print(f"📊 Loudness LineData 생성 완료: {len(data_points)}개 포인트")
        print(f"   - Loudness 범위: {min_value:.1f}{unit} ~ {max_value:.1f}{unit}")
        print(f"   - Y축 범위: {actual_y_min} ~ {actual_y_max}")
        print(f"   - 렌더링 모드: 전체 grid canvas 높이 (independent_range)")

        return line_data

    except Exception as e:
        print(f"❌ Loudness LineData 생성 오류: {e}")
        return None

def create_voicing_line_data(voicing_data, tempo=120, pixelsPerBeat=80, use_probs=True):
    """
    Voice/Unvoice 데이터를 LineLayer용 line_data 형식으로 변환합니다.
    독립적인 Y축 범위를 가지며 0(unvoiced) ~ 1(voiced) 범위로 표시됩니다.
    """
    if not voicing_data:
        return None

    try:
        times = voicing_data['times']

        # 사용할 voicing 값 선택 (확률값 또는 이진값)
        if use_probs and 'voiced_probs' in voicing_data:
            values = voicing_data['voiced_probs']
            unit = "probability"
        else:
            values = voicing_data['voiced_flag'].astype(float)
            unit = "binary"

        # 데이터 포인트 생성
        data_points = []
        for time, value in zip(times, values):
            if not np.isnan(value):
                # 시간(초)을 픽셀 X 좌표로 변환
                x_pixel = time * (tempo / 60) * pixelsPerBeat

                # Voice/Unvoice 값을 0-2560 픽셀 범위로 변환 (전체 grid canvas 높이 사용)
                y_pixel = value * 2560  # 0-1 범위를 0-2560 픽셀로

                data_points.append({
                    "x": float(x_pixel),
                    "y": float(max(0, min(2560, y_pixel)))  # 범위 제한
                })

        if not data_points:
            print("⚠️ 유효한 Voice/Unvoice 데이터 포인트가 없습니다.")
            return None

        # 실제 값 범위
        min_value = float(np.min(values))
        max_value = float(np.max(values))
        voiced_ratio = voicing_data.get('voiced_ratio', 0.0)

        line_data = {
            "voicing_curve": {
                "color": "#9B59B6",  # 보라색
                "lineWidth": 2,
                "yMin": 0,
                "yMax": 2560,  # 전체 grid canvas 높이 (128개 노트 * 20픽셀)
                "position": "overlay",  # 전체 영역에 오버레이로 표시
                "renderMode": "independent_range",  # 독립적인 Y축 범위
                "visible": True,
                "opacity": 0.6,
                "data": data_points,
                # 메타데이터
                "dataType": "voicing",
                "unit": unit,
                "originalRange": {
                    "min": min_value,
                    "max": max_value,
                    "voiced_ratio": voiced_ratio,
                    "y_min": 0,
                    "y_max": 1
                }
            }
        }

        print(f"📊 Voice/Unvoice LineData 생성 완료: {len(data_points)}개 포인트")
        print(f"   - Voice/Unvoice 범위: {min_value:.3f} ~ {max_value:.3f} ({unit})")
        print(f"   - Voiced 비율: {voiced_ratio:.1%}")
        print(f"   - 렌더링 모드: 전체 grid canvas 높이 (independent_range)")

        return line_data

    except Exception as e:
        print(f"❌ Voice/Unvoice LineData 생성 오류: {e}")
        return None

def create_multi_feature_line_data(features, tempo=120, pixelsPerBeat=80,
                                   loudness_y_min=None, loudness_y_max=None,
                                   loudness_use_db=True, voicing_use_probs=True):
    """
    여러 오디오 특성(F0, Loudness, Voice/Unvoice 등)을 하나의 line_data로 결합합니다.
    """
    combined_line_data = {}

    try:
        # F0 곡선 추가
        if 'f0' in features:
            f0_line_data = create_f0_line_data(features['f0'], tempo, pixelsPerBeat)
            if f0_line_data:
                combined_line_data.update(f0_line_data)

        # Loudness 곡선 추가
        if 'loudness' in features:
            loudness_line_data = create_loudness_line_data(
                features['loudness'], tempo, pixelsPerBeat,
                loudness_y_min, loudness_y_max, loudness_use_db
            )
            if loudness_line_data:
                combined_line_data.update(loudness_line_data)

        # Voice/Unvoice 곡선 추가
        if 'voicing' in features:
            voicing_line_data = create_voicing_line_data(
                features['voicing'], tempo, pixelsPerBeat, voicing_use_probs
            )
            if voicing_line_data:
                combined_line_data.update(voicing_line_data)

        if combined_line_data:
            print(f"📊 통합 LineData 생성 완료: {len(combined_line_data)}개 곡선")
            return combined_line_data
        else:
            print("⚠️ 생성된 곡선 데이터가 없습니다.")
            return None

    except Exception as e:
        print(f"❌ 통합 LineData 생성 오류: {e}")
        return None

def synthesize_and_analyze_features(piano_roll, attack, decay, sustain, release, wave_type='complex',
                                  include_f0=True, include_loudness=True, include_voicing=True, f0_method="pyin",
                                  loudness_y_min=None, loudness_y_max=None, loudness_use_db=True, voicing_use_probs=True):
    """
    피아노롤에서 오디오를 생성하고, 생성된 오디오에서 F0, loudness, voice/unvoice를 분석하여 시각화합니다.
    """
    print("=== Synthesize and Analyze Features ===")
    print(f"ADSR: A={attack}, D={decay}, S={sustain}, R={release}")
    print(f"Wave Type: {wave_type}")
    print(f"Include F0: {include_f0}, Include Loudness: {include_loudness}, Include Voicing: {include_voicing}")

    # 먼저 오디오 합성
    audio_data = synthesize_audio(piano_roll, attack, decay, sustain, release, wave_type)

    if audio_data is None:
        return piano_roll, "오디오 생성 실패", None

    # 임시 WAV 파일 생성
    temp_audio_path = create_temp_wav_file(audio_data, SAMPLE_RATE)
    if temp_audio_path is None:
        return piano_roll, "임시 오디오 파일 생성 실패", None

    try:
        # 오디오 특성 분석
        features, analysis_status = extract_audio_features(
            temp_audio_path, f0_method, include_f0, include_loudness, include_voicing
        )

        if features is None:
            return piano_roll, f"오디오 특성 분석 실패: {analysis_status}", temp_audio_path

        # 피아노롤 업데이트
        updated_piano_roll = piano_roll.copy() if piano_roll else {}

        # 백엔드 오디오 데이터 추가
        audio_base64 = audio_to_base64_wav(audio_data, SAMPLE_RATE)
        updated_piano_roll['audio_data'] = audio_base64
        updated_piano_roll['use_backend_audio'] = True

        # 템포와 픽셀당 비트 정보
        tempo = updated_piano_roll.get('tempo', 120)
        pixels_per_beat = updated_piano_roll.get('pixelsPerBeat', 80)

        # 웨이브폼 데이터 계산 (백엔드 오디오용)
        waveform_data = calculate_waveform_data(audio_data, pixels_per_beat, tempo)

        # 곡선 데이터 생성 (오디오 특성 분석 결과)
        line_data = create_multi_feature_line_data(
            features, tempo, pixels_per_beat,
            loudness_y_min, loudness_y_max, loudness_use_db, voicing_use_probs
        )

        # 통합 곡선 데이터 설정 (오디오 특성 + 웨이브폼)
        curve_data = {}

        # 오디오 특성 곡선 추가
        if line_data:
            curve_data.update(line_data)

        # 웨이브폼 데이터 추가
        if waveform_data:
            curve_data['waveform_data'] = waveform_data
            print(f"웨이브폼 데이터 생성: {len(waveform_data)} 포인트")

        # 피아노롤에 곡선 데이터 설정
        if curve_data:
            updated_piano_roll['curve_data'] = curve_data

        # line_data도 별도로 설정 (LineLayer용)
        if line_data:
            updated_piano_roll['line_data'] = line_data

        print(f"🔊 [synthesize_and_analyze_features] Setting backend audio data:")
        print(f"   - audio_data length: {len(audio_base64) if audio_base64 else 0}")
        print(f"   - use_backend_audio: {updated_piano_roll['use_backend_audio']}")
        print(f"   - waveform points: {len(waveform_data) if waveform_data else 0}")
        print(f"   - feature curves: {len(line_data) if line_data else 0}")

        # 상태 메시지 생성
        status_parts = [f"오디오 합성 완료 ({wave_type} 파형)", analysis_status]

        if waveform_data:
            status_parts.append(f"웨이브폼 시각화 완료 ({len(waveform_data)}개 포인트)")

        if line_data:
            curve_count = len(line_data)
            status_parts.append(f"{curve_count}개 특성 곡선 시각화 완료")

        status_message = " | ".join(status_parts)

        return updated_piano_roll, status_message, temp_audio_path

    except Exception as e:
        error_message = f"특성 분석 중 오류: {str(e)}"
        print(f"❌ {error_message}")
        return piano_roll, error_message, temp_audio_path
    # 임시 파일은 사용 후 별도로 정리 (gradio가 자동 관리)

def analyze_uploaded_audio_features(piano_roll, audio_file, include_f0=True, include_loudness=True, include_voicing=True,
                                  f0_method="pyin", loudness_y_min=None, loudness_y_max=None,
                                  loudness_use_db=True, voicing_use_probs=True):
    """
    업로드된 오디오 파일에서 F0, loudness, voice/unvoice를 분석하고 피아노롤에 표시합니다.
    """
    print("=== Analyze Uploaded Audio Features ===")
    print(f"Audio file: {audio_file}")
    print(f"Include F0: {include_f0}, Include Loudness: {include_loudness}, Include Voicing: {include_voicing}")

    if not audio_file:
        return piano_roll, "오디오 파일을 업로드해주세요.", None

    if not LIBROSA_AVAILABLE:
        return piano_roll, "librosa가 설치되지 않아 오디오 특성 분석을 수행할 수 없습니다. 'pip install librosa'로 설치해주세요.", None

    try:
        # 오디오 특성 분석
        features, analysis_status = extract_audio_features(
            audio_file, f0_method, include_f0, include_loudness, include_voicing
        )

        if features is None:
            return piano_roll, f"오디오 특성 분석 실패: {analysis_status}", audio_file

        # 피아노롤 데이터 업데이트
        updated_piano_roll = piano_roll.copy() if piano_roll else {
            "notes": [],
            "tempo": 120,
            "timeSignature": {"numerator": 4, "denominator": 4},
            "editMode": "select",
            "snapSetting": "1/4",
            "pixelsPerBeat": 80
        }

        # 곡선 데이터 생성
        tempo = updated_piano_roll.get('tempo', 120)
        pixels_per_beat = updated_piano_roll.get('pixelsPerBeat', 80)

        line_data = create_multi_feature_line_data(
            features, tempo, pixels_per_beat,
            loudness_y_min, loudness_y_max, loudness_use_db, voicing_use_probs
        )

        if line_data:
            updated_piano_roll['line_data'] = line_data

        # 상태 메시지 생성
        status_parts = [analysis_status]

        if line_data:
            curve_count = len(line_data)
            curve_types = list(line_data.keys())
            status_parts.append(f"{curve_count}개 곡선 ({', '.join(curve_types)}) 시각화 완료")

            # 각 특성의 범위 정보 추가
            for curve_name, curve_info in line_data.items():
                if 'originalRange' in curve_info:
                    range_info = curve_info['originalRange']
                    if 'minHz' in range_info:  # F0
                        status_parts.append(f"F0: {range_info['minHz']:.1f}~{range_info['maxHz']:.1f}Hz")
                    elif 'min' in range_info and 'voiced_ratio' not in range_info:  # Loudness
                        unit = curve_info.get('unit', '')
                        status_parts.append(f"Loudness: {range_info['min']:.1f}~{range_info['max']:.1f}{unit}")
                    elif 'voiced_ratio' in range_info:  # Voice/Unvoice
                        unit = curve_info.get('unit', '')
                        voiced_ratio = range_info['voiced_ratio']
                        status_parts.append(f"Voicing: {voiced_ratio:.1%} voiced ({unit})")

        duration = features.get('duration', 0)
        status_parts.append(f"⏱️ {duration:.2f}초")

        status_message = " | ".join(status_parts)

        return updated_piano_roll, status_message, audio_file

    except Exception as e:
        error_message = f"업로드된 오디오 분석 중 오류: {str(e)}"
        print(f"❌ {error_message}")
        return piano_roll, error_message, audio_file

def analyze_audio_f0(piano_roll, audio_file, f0_method="pyin"):
    """
    업로드된 오디오 파일에서 F0를 추출하고 피아노롤에 표시합니다. (기존 호환성 유지)
    """
    return analyze_uploaded_audio_features(
        piano_roll, audio_file, include_f0=True, include_loudness=False, include_voicing=False, f0_method=f0_method
    )

def generate_f0_demo_audio():
    """
    F0 분석 데모용 간단한 오디오를 생성합니다.
    """
    print("🎵 F0 데모 오디오 생성 중...")

    # 간단한 스위프 톤 생성 (100Hz에서 400Hz까지)
    duration = 3.0  # 3초
    sample_rate = 44100
    t = np.linspace(0, duration, int(duration * sample_rate), False)

    # 주파수가 시간에 따라 변하는 사인파 (100Hz -> 400Hz)
    start_freq = 100
    end_freq = 400
    instantaneous_freq = start_freq + (end_freq - start_freq) * (t / duration)

    # 주파수 변조된 사인파 생성
    phase = 2 * np.pi * np.cumsum(instantaneous_freq) / sample_rate
    audio = 0.3 * np.sin(phase)  # 볼륨 조절

    # WAV 파일로 저장
    temp_fd, temp_path = tempfile.mkstemp(suffix='.wav')
    try:
        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # 모노
            wav_file.setsampwidth(2)  # 16비트
            wav_file.setframerate(sample_rate)

            # 16비트 PCM으로 변환
            audio_16bit = (audio * 32767).astype(np.int16)
            wav_file.writeframes(audio_16bit.tobytes())

        os.close(temp_fd)
        print(f"✅ 데모 오디오 생성 완료: {temp_path}")
        return temp_path

    except Exception as e:
        os.close(temp_fd)
        print(f"❌ 데모 오디오 생성 실패: {e}")
        return None

def generate_feature_demo_audio():
    """
    오디오 특성 분석 데모용 다양한 특성을 가진 오디오를 생성합니다.
    F0 변화와 loudness 변화를 모두 포함합니다.
    """
    print("🎵 오디오 특성 분석 데모 오디오 생성 중...")

    duration = 4.0  # 4초
    sample_rate = 44100
    t = np.linspace(0, duration, int(duration * sample_rate), False)

    # 구간별로 다른 특성을 가진 오디오 생성
    audio = np.zeros_like(t)

    # 구간 1 (0-1초): C4에서 C5로 상승 + 볼륨 증가
    mask1 = (t >= 0) & (t < 1)
    t1 = t[mask1]
    f1_start, f1_end = 261.63, 523.25  # C4 to C5
    freq1 = f1_start + (f1_end - f1_start) * (t1 / 1.0)
    phase1 = 2 * np.pi * np.cumsum(freq1) / sample_rate
    vol1 = 0.1 + 0.4 * (t1 / 1.0)  # 0.1에서 0.5로 증가
    audio[mask1] = vol1 * np.sin(phase1)

    # 구간 2 (1-2초): C5에서 G4로 하강 + 일정한 볼륨
    mask2 = (t >= 1) & (t < 2)
    t2 = t[mask2] - 1
    f2_start, f2_end = 523.25, 392.00  # C5 to G4
    freq2 = f2_start + (f2_end - f2_start) * (t2 / 1.0)
    phase2 = 2 * np.pi * np.cumsum(freq2) / sample_rate
    audio[mask2] = 0.5 * np.sin(phase2)

    # 구간 3 (2-3초): A4 고정 + 볼륨 감소 (트레몰로 효과)
    mask3 = (t >= 2) & (t < 3)
    t3 = t[mask3] - 2
    freq3 = 440.0  # A4 고정
    phase3 = 2 * np.pi * freq3 * t3
    vol3 = 0.5 * (1 - t3 / 1.0) * (1 + 0.3 * np.sin(2 * np.pi * 6 * t3))  # 트레몰로
    audio[mask3] = vol3 * np.sin(phase3)

    # 구간 4 (3-4초): 복합음 (A4 + E5) + 페이드아웃
    mask4 = (t >= 3) & (t < 4)
    t4 = t[mask4] - 3
    freq4a, freq4b = 440.0, 659.25  # A4 + E5
    phase4a = 2 * np.pi * freq4a * t4
    phase4b = 2 * np.pi * freq4b * t4
    vol4 = 0.4 * (1 - t4 / 1.0)  # 페이드아웃
    audio[mask4] = vol4 * (0.6 * np.sin(phase4a) + 0.4 * np.sin(phase4b))

    # WAV 파일로 저장
    temp_fd, temp_path = tempfile.mkstemp(suffix='.wav')
    try:
        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # 모노
            wav_file.setsampwidth(2)  # 16비트
            wav_file.setframerate(sample_rate)

            # 16비트 PCM으로 변환
            audio_16bit = (audio * 32767).astype(np.int16)
            wav_file.writeframes(audio_16bit.tobytes())

        os.close(temp_fd)
        print(f"✅ 오디오 특성 분석 데모 오디오 생성 완료: {temp_path}")
        return temp_path

    except Exception as e:
        os.close(temp_fd)
        print(f"❌ 오디오 특성 분석 데모 오디오 생성 실패: {e}")
        return None

# Gradio 인터페이스
with gr.Blocks(title="PianoRoll with Synthesizer Demo") as demo:
    gr.Markdown("# 🎹 Gradio PianoRoll with Synthesizer")
    gr.Markdown("피아노롤 컴포넌트와 신디사이저 기능을 테스트해보세요!")

    with gr.Tabs():
        # 첫 번째 탭: 기본 데모
        with gr.TabItem("🎼 Basic Demo"):
            gr.Markdown("## 기본 피아노롤 데모")

            with gr.Row():
                with gr.Column():
                    # 초기값 설정
                    initial_value_basic = {
                        "notes": [
                            {
                                "start": 80,
                                "duration": 80,
                                "pitch": 60,
                                "velocity": 100,
                                "lyric": "안녕"
                            },
                            {
                                "start": 160,
                                "duration": 160,
                                "pitch": 64,
                                "velocity": 90,
                                "lyric": "하세요"
                            }
                        ],
                        "tempo": 120,
                        "timeSignature": {"numerator": 4, "denominator": 4},
                        "editMode": "select",
                        "snapSetting": "1/4"
                    }
                    piano_roll_basic = PianoRoll(
                        height=600,
                        width=1000,
                        value=initial_value_basic,
                        elem_id="piano_roll_basic",  # 고유 ID 부여
                        use_backend_audio=False  # 프론트엔드 오디오 엔진 사용
                    )

            with gr.Row():
                with gr.Column():
                    output_json_basic = gr.JSON()

            with gr.Row():
                with gr.Column():
                    btn_basic = gr.Button("🔄 Convert & Debug", variant="primary")

            # 기본 탭 이벤트
            btn_basic.click(
                fn=convert_basic,
                inputs=piano_roll_basic,
                outputs=output_json_basic,
                show_progress=True
            )

        # 두 번째 탭: 신디사이저 데모
        with gr.TabItem("🎵 Synthesizer Demo"):
            gr.Markdown("## 신디사이저가 포함된 피아노롤 데모")
            gr.Markdown("노트를 편집한 후 '🎶 Synthesize Audio' 버튼을 클릭하면 오디오가 생성되어 재생됩니다!")

            with gr.Row():
                with gr.Column(scale=3):
                    # 신디사이저용 초기값
                    initial_value_synth = {
                        "notes": [
                            {
                                "start": 0,
                                "duration": 160,
                                "pitch": 60,  # C4
                                "velocity": 100,
                                "lyric": "도"
                            },
                            {
                                "start": 160,
                                "duration": 160,
                                "pitch": 62,  # D4
                                "velocity": 100,
                                "lyric": "레"
                            },
                            {
                                "start": 320,
                                "duration": 160,
                                "pitch": 64,  # E4
                                "velocity": 100,
                                "lyric": "미"
                            },
                            {
                                "start": 480,
                                "duration": 160,
                                "pitch": 65,  # F4
                                "velocity": 100,
                                "lyric": "파"
                            }
                        ],
                        "tempo": 120,
                        "timeSignature": {"numerator": 4, "denominator": 4},
                        "editMode": "select",
                        "snapSetting": "1/4",
                        "curve_data": {},  # 초기에는 빈 곡선 데이터
                        "use_backend_audio": False  # 초기에는 백엔드 오디오 비활성화
                    }
                    piano_roll_synth = PianoRoll(
                        height=600,
                        width=1000,
                        value=initial_value_synth,
                        elem_id="piano_roll_synth",  # 고유 ID 부여
                        use_backend_audio=False  # 초기에는 프론트엔드 엔진 사용, synthesize 시 백엔드로 전환
                    )

                with gr.Column(scale=1):
                    gr.Markdown("### 🎛️ ADSR 설정")
                    attack_slider = gr.Slider(
                        minimum=0.001,
                        maximum=1.0,
                        value=0.01,
                        step=0.001,
                        label="Attack (초)"
                    )
                    decay_slider = gr.Slider(
                        minimum=0.001,
                        maximum=1.0,
                        value=0.1,
                        step=0.001,
                        label="Decay (초)"
                    )
                    sustain_slider = gr.Slider(
                        minimum=0.0,
                        maximum=1.0,
                        value=0.7,
                        step=0.01,
                        label="Sustain (레벨)"
                    )
                    release_slider = gr.Slider(
                        minimum=0.001,
                        maximum=2.0,
                        value=0.3,
                        step=0.001,
                        label="Release (초)"
                    )

                    gr.Markdown("### 🎵 파형 설정")
                    wave_type_dropdown = gr.Dropdown(
                        choices=[
                            ("복합 파형 (Complex)", "complex"),
                            ("하모닉 합성 (Harmonic)", "harmonic"),
                            ("FM 합성 (FM)", "fm"),
                            ("톱니파 (Sawtooth)", "sawtooth"),
                            ("사각파 (Square)", "square"),
                            ("삼각파 (Triangle)", "triangle"),
                            ("사인파 (Sine)", "sine")
                        ],
                        value="complex",
                        label="파형 타입",
                        info="각 노트는 순환적으로 다른 파형을 사용합니다"
                    )

            with gr.Row():
                with gr.Column():
                    btn_synthesize = gr.Button("🎶 Synthesize Audio", variant="primary", size="lg")
                    status_text = gr.Textbox(label="상태", interactive=False)

            with gr.Row():
                with gr.Column():
                    btn_regenerate = gr.Button("🔄 웨이브폼 재생성", variant="secondary", size="lg")

            # 비교용 gradio Audio 컴포넌트 추가
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 🔊 비교용 Gradio Audio 재생")
                    gradio_audio_output = gr.Audio(
                        label="백엔드에서 생성된 오디오 (비교용)",
                        type="filepath",
                        interactive=False
                    )

            with gr.Row():
                with gr.Column():
                    output_json_synth = gr.JSON(label="결과 데이터")

            # 신디사이저 탭 이벤트
            btn_synthesize.click(
                fn=synthesize_and_play,
                inputs=[
                    piano_roll_synth,
                    attack_slider,
                    decay_slider,
                    sustain_slider,
                    release_slider,
                    wave_type_dropdown
                ],
                outputs=[piano_roll_synth, status_text, gradio_audio_output],
                show_progress=True
            )

            # 웨이브폼 재생성 버튼 이벤트
            btn_regenerate.click(
                fn=clear_and_regenerate_waveform,
                inputs=[
                    piano_roll_synth,
                    attack_slider,
                    decay_slider,
                    sustain_slider,
                    release_slider,
                    wave_type_dropdown
                ],
                outputs=[piano_roll_synth, status_text, gradio_audio_output],
                show_progress=True
            )

            # 이벤트 리스너 설정
            def log_play_event(event_data=None):
                print("🎵 Play event triggered:", event_data)
                return f"재생 시작됨: {event_data if event_data else '재생 중'}"

            def log_pause_event(event_data=None):
                print("⏸️ Pause event triggered:", event_data)
                return f"일시정지됨: {event_data if event_data else '일시정지'}"

            def log_stop_event(event_data=None):
                print("⏹️ Stop event triggered:", event_data)
                return f"정지됨: {event_data if event_data else '정지'}"

            piano_roll_synth.play(log_play_event, outputs=status_text)
            piano_roll_synth.pause(log_pause_event, outputs=status_text)
            piano_roll_synth.stop(log_stop_event, outputs=status_text)

            # input 이벤트 처리 추가 (G2P 처리)
            def handle_synth_input(lyric_data):
                print("🎵 Synthesizer tab - Input event triggered:", lyric_data)
                return f"가사 입력 감지: {lyric_data if lyric_data else '입력됨'}"

            piano_roll_synth.input(handle_synth_input, outputs=status_text)

            # 노트 변경 시 JSON 출력 업데이트
            piano_roll_synth.change(lambda x: x, inputs=piano_roll_synth, outputs=output_json_synth)

        # 세 번째 탭: Phoneme 데모
        with gr.TabItem("🗣️ Phoneme Demo"):
            gr.Markdown("## 📢 음소(Phoneme) 기능 데모")
            gr.Markdown("가사를 수정하면 자동으로 G2P(Grapheme-to-Phoneme)가 실행되어 음소가 표시됩니다. 또한 수동으로 음소를 편집할 수도 있습니다.")

            with gr.Row():
                with gr.Column(scale=3):
                    # Phoneme용 초기값
                    initial_value_phoneme = {
                        "notes": [
                            {
                                "id": "note_0",
                                "start": 0,
                                "duration": 160,
                                "pitch": 60,  # C4
                                "velocity": 100,
                                "lyric": "안녕",
                                "phoneme": "aa n ny eo ng"  # 미리 설정된 음소
                            },
                            {
                                "id": "note_1",
                                "start": 160,
                                "duration": 160,
                                "pitch": 62,  # D4
                                "velocity": 100,
                                "lyric": "하세요",
                                "phoneme": "h a s e y o"
                            },
                            {
                                "id": "note_2",
                                "start": 320,
                                "duration": 160,
                                "pitch": 64,  # E4
                                "velocity": 100,
                                "lyric": "음악",
                                "phoneme": "eu m a k"
                            },
                            {
                                "id": "note_3",
                                "start": 480,
                                "duration": 160,
                                "pitch": 65,  # F4
                                "velocity": 100,
                                "lyric": "피아노"
                            }
                        ],
                        "tempo": 120,
                        "timeSignature": {"numerator": 4, "denominator": 4},
                        "editMode": "select",
                        "snapSetting": "1/4"
                    }
                    piano_roll_phoneme = PianoRoll(
                        height=600,
                        width=1000,
                        value=initial_value_phoneme,
                        elem_id="piano_roll_phoneme",  # 고유 ID 부여
                        use_backend_audio=False  # 프론트엔드 오디오 엔진 사용
                    )

                with gr.Column(scale=1):
                    gr.Markdown("### 📝 Phoneme 매핑 관리")

                    # 현재 매핑 리스트 표시
                    phoneme_mapping_dataframe = gr.Dataframe(
                        headers=["가사", "Phoneme"],
                        datatype=["str", "str"],
                        value=get_phoneme_mapping_for_dataframe(),
                        label="현재 Phoneme 매핑",
                        interactive=True,
                        wrap=True
                    )

                    gr.Markdown("#### ➕ 새 매핑 추가")
                    with gr.Row():
                        add_lyric_input = gr.Textbox(
                            label="가사",
                            placeholder="예: 라",
                            scale=1
                        )
                        add_phoneme_input = gr.Textbox(
                            label="Phoneme",
                            placeholder="예: l aa",
                            scale=1
                        )
                    btn_add_mapping = gr.Button("➕ 매핑 추가", variant="primary", size="sm")

                    gr.Markdown("### 🔧 일괄 작업")
                    with gr.Row():
                        btn_auto_generate = gr.Button("🤖 모든 Phoneme 자동 생성", variant="primary")
                        btn_clear_phonemes = gr.Button("🗑️ 모든 Phoneme 지우기", variant="secondary")

                    btn_reset_mapping = gr.Button("🔄 매핑 기본값으로 리셋", variant="secondary")

            with gr.Row():
                with gr.Column():
                    phoneme_status_text = gr.Textbox(label="상태", interactive=False)

            with gr.Row():
                with gr.Column():
                    output_json_phoneme = gr.JSON(label="Phoneme 데이터")

            # Phoneme 탭 이벤트 처리

            # 매핑 추가
            btn_add_mapping.click(
                fn=add_phoneme_mapping,
                inputs=[add_lyric_input, add_phoneme_input],
                outputs=[phoneme_mapping_dataframe, phoneme_status_text],
                show_progress=False
            ).then(
                fn=lambda: ["", ""],  # 입력 필드 초기화
                outputs=[add_lyric_input, add_phoneme_input]
            )

            # 매핑 리셋
            btn_reset_mapping.click(
                fn=reset_phoneme_mapping,
                outputs=[phoneme_mapping_dataframe, phoneme_status_text],
                show_progress=False
            )

            # 가사 입력 시 자동 G2P 처리
            def handle_phoneme_input_event(piano_roll_data):
                """가사 입력 이벤트 처리 - 피아노롤 변경사항을 감지하여 phoneme 생성"""
                print("🗣️ Phoneme tab - Input event triggered")
                print(f"   - Piano roll data: {type(piano_roll_data)}")

                if not piano_roll_data or 'notes' not in piano_roll_data:
                    return piano_roll_data, "피아노롤 데이터가 없습니다."

                return auto_generate_missing_phonemes(piano_roll_data)

            def auto_generate_missing_phonemes(piano_roll_data):
                """가사가 있지만 phoneme이 없는 노트들에 대해 자동으로 phoneme 생성"""
                if not piano_roll_data or 'notes' not in piano_roll_data:
                    return piano_roll_data, "피아노롤 데이터가 없습니다."

                # 현재 notes를 복사
                notes = piano_roll_data['notes'].copy()
                updated_notes = []
                changes_made = 0

                for note in notes:
                    note_copy = note.copy()

                    # 가사가 있는 경우 처리
                    lyric = note.get('lyric', '').strip()
                    current_phoneme = note.get('phoneme', '').strip()

                    if lyric:
                        # G2P 실행하여 새로운 phoneme 생성
                        new_phoneme = mock_g2p(lyric)

                        # 기존 phoneme과 다르거나 없으면 업데이트
                        if not current_phoneme or current_phoneme != new_phoneme:
                            note_copy['phoneme'] = new_phoneme
                            changes_made += 1
                            print(f"   - G2P 적용: '{lyric}' -> '{new_phoneme}'")
                    else:
                        # 가사가 없으면 phoneme도 제거
                        if current_phoneme:
                            note_copy['phoneme'] = None
                            changes_made += 1
                            print(f"   - Phoneme 제거 (가사 없음)")

                    updated_notes.append(note_copy)

                if changes_made > 0:
                    # 업데이트된 피아노롤 데이터 반환
                    updated_piano_roll = piano_roll_data.copy()
                    updated_piano_roll['notes'] = updated_notes
                    return updated_piano_roll, f"자동 G2P 완료: {changes_made}개 노트 업데이트"
                else:
                    return piano_roll_data, "G2P 적용할 변경사항이 없습니다."

            piano_roll_phoneme.input(
                fn=handle_phoneme_input_event,
                inputs=[piano_roll_phoneme],
                outputs=[piano_roll_phoneme, phoneme_status_text],
                show_progress=False
            )

            # 노트 변경 시에도 자동 phoneme 생성
            def handle_phoneme_change_event(piano_roll_data):
                """피아노롤 변경 시 자동 phoneme 처리"""
                return auto_generate_missing_phonemes(piano_roll_data)

            piano_roll_phoneme.change(
                fn=handle_phoneme_change_event,
                inputs=[piano_roll_phoneme],
                outputs=[piano_roll_phoneme, phoneme_status_text],
                show_progress=False
            )

            # 자동 phoneme 생성 (수동 버튼)
            btn_auto_generate.click(
                fn=auto_generate_all_phonemes,
                inputs=[piano_roll_phoneme],
                outputs=[piano_roll_phoneme, phoneme_status_text],
                show_progress=True
            )

            # 모든 phoneme 지우기
            btn_clear_phonemes.click(
                fn=clear_all_phonemes,
                inputs=[piano_roll_phoneme],
                outputs=[piano_roll_phoneme, phoneme_status_text],
                show_progress=False
            )

            # 노트 변경 시 JSON 출력 업데이트 (자동 phoneme 처리와 별도로)
            def update_json_output(piano_roll_data):
                return piano_roll_data

            piano_roll_phoneme.change(
                fn=update_json_output,
                inputs=[piano_roll_phoneme],
                outputs=[output_json_phoneme],
                show_progress=False
            )

            # 재생 이벤트 로깅
            def log_phoneme_play_event(event_data=None):
                print("🗣️ Phoneme Play event triggered:", event_data)
                return f"재생 시작: {event_data if event_data else '재생 중'}"

            def log_phoneme_pause_event(event_data=None):
                print("🗣️ Phoneme Pause event triggered:", event_data)
                return f"일시정지: {event_data if event_data else '일시정지'}"

            def log_phoneme_stop_event(event_data=None):
                print("🗣️ Phoneme Stop event triggered:", event_data)
                return f"정지: {event_data if event_data else '정지'}"

            piano_roll_phoneme.play(log_phoneme_play_event, outputs=phoneme_status_text)
            piano_roll_phoneme.pause(log_phoneme_pause_event, outputs=phoneme_status_text)
            piano_roll_phoneme.stop(log_phoneme_stop_event, outputs=phoneme_status_text)

        # 네 번째 탭: F0 분석 데모
        with gr.TabItem("📊 F0 Analysis Demo"):
            gr.Markdown("## 🎵 F0 (Fundamental Frequency) 분석 데모")
            if LIBROSA_AVAILABLE:
                gr.Markdown("오디오 파일을 업로드하고 F0를 추출하여 피아노롤에서 시각화해보세요!")
            else:
                gr.Markdown("⚠️ **librosa가 설치되지 않음**: F0 분석을 위해 `pip install librosa`를 실행해주세요.")

            with gr.Row():
                with gr.Column(scale=3):
                    # F0용 초기값 (빈 피아노롤)
                    initial_value_f0 = {
                        "notes": [],
                        "tempo": 120,
                        "timeSignature": {"numerator": 4, "denominator": 4},
                        "editMode": "select",
                        "snapSetting": "1/4",
                        "pixelsPerBeat": 80
                    }
                    piano_roll_f0 = PianoRoll(
                        height=600,
                        width=1000,
                        value=initial_value_f0,
                        elem_id="piano_roll_f0",  # 고유 ID 부여
                        use_backend_audio=False  # 프론트엔드 오디오 엔진 사용
                    )

                with gr.Column(scale=1):
                    gr.Markdown("### 🎤 오디오 업로드")

                    audio_input = gr.Audio(
                        label="분석할 오디오 파일",
                        type="filepath",
                        interactive=True
                    )

                    gr.Markdown("### ⚙️ F0 추출 설정")
                    f0_method_dropdown = gr.Dropdown(
                        choices=[
                            ("PYIN (정확함, 느림)", "pyin"),
                            ("PipTrack (빠름, 덜 정확)", "piptrack")
                        ],
                        value="pyin",
                        label="F0 추출 방법"
                    )
                    gr.Markdown("💡 **PYIN**은 더 정확하지만 처리 시간이 길어집니다.")

                    btn_analyze_f0 = gr.Button(
                        "🔬 F0 분석 시작",
                        variant="primary",
                        size="lg",
                        interactive=LIBROSA_AVAILABLE
                    )

                    btn_generate_demo = gr.Button(
                        "🎵 데모 오디오 생성",
                        variant="secondary"
                    )
                    gr.Markdown("📄 F0가 시간에 따라 변하는 테스트 오디오를 생성합니다.")

                    if not LIBROSA_AVAILABLE:
                        gr.Markdown("⚠️ librosa가 필요합니다")

            with gr.Row():
                with gr.Column():
                    f0_status_text = gr.Textbox(
                        label="분석 상태",
                        interactive=False,
                        lines=6
                    )

            with gr.Row():
                with gr.Column():
                    # 비교용 오디오 재생
                    reference_audio = gr.Audio(
                        label="원본 오디오 (참고용)",
                        type="filepath",
                        interactive=False
                    )

            with gr.Row():
                with gr.Column():
                    output_json_f0 = gr.JSON(label="F0 분석 결과")

            # F0 탭 이벤트 처리

            # F0 분석 버튼
            btn_analyze_f0.click(
                fn=analyze_audio_f0,
                inputs=[piano_roll_f0, audio_input, f0_method_dropdown],
                outputs=[piano_roll_f0, f0_status_text, reference_audio],
                show_progress=True
            )

            # 데모 오디오 생성 버튼
            def create_and_analyze_demo():
                """데모 오디오를 생성하고 자동으로 F0 분석을 수행합니다."""
                demo_audio_path = generate_f0_demo_audio()
                if demo_audio_path:
                    # 초기 피아노롤 데이터
                    initial_piano_roll = {
                        "notes": [],
                        "tempo": 120,
                        "timeSignature": {"numerator": 4, "denominator": 4},
                        "editMode": "select",
                        "snapSetting": "1/4",
                        "pixelsPerBeat": 80
                    }

                    # F0 분석 수행
                    updated_piano_roll, status, _ = analyze_audio_f0(initial_piano_roll, demo_audio_path, "pyin")

                    return updated_piano_roll, status, demo_audio_path, demo_audio_path
                else:
                    return initial_value_f0, "데모 오디오 생성에 실패했습니다.", None, None

            btn_generate_demo.click(
                fn=create_and_analyze_demo,
                outputs=[piano_roll_f0, f0_status_text, audio_input, reference_audio],
                show_progress=True
            )

            # 노트 변경 시 JSON 출력 업데이트
            def update_f0_json_output(piano_roll_data):
                return piano_roll_data

            piano_roll_f0.change(
                fn=update_f0_json_output,
                inputs=[piano_roll_f0],
                outputs=[output_json_f0],
                show_progress=False
            )

            # 재생 이벤트 로깅
            def log_f0_play_event(event_data=None):
                print("📊 F0 Play event triggered:", event_data)
                return f"재생 시작: {event_data if event_data else '재생 중'}"

            def log_f0_pause_event(event_data=None):
                print("📊 F0 Pause event triggered:", event_data)
                return f"일시정지: {event_data if event_data else '일시정지'}"

            def log_f0_stop_event(event_data=None):
                print("📊 F0 Stop event triggered:", event_data)
                return f"정지: {event_data if event_data else '정지'}"

            piano_roll_f0.play(log_f0_play_event, outputs=f0_status_text)
            piano_roll_f0.pause(log_f0_pause_event, outputs=f0_status_text)
            piano_roll_f0.stop(log_f0_stop_event, outputs=f0_status_text)

        # 다섯 번째 탭: 오디오 특성 분석 데모
        with gr.TabItem("🔊 Audio Feature Analysis"):
            gr.Markdown("## 🎵 오디오 특성 분석 데모")
            if LIBROSA_AVAILABLE:
                gr.Markdown("피아노롤 노트에서 오디오를 생성하고 F0와 loudness를 분석하거나, 직접 오디오를 업로드해서 분석해보세요!")
            else:
                gr.Markdown("⚠️ **librosa가 설치되지 않음**: 오디오 특성 분석을 위해 `pip install librosa`를 실행해주세요.")

            with gr.Row():
                with gr.Column(scale=3):
                    # 오디오 특성 분석용 초기값
                    initial_value_features = {
                        "notes": [
                            {
                                "start": 0,
                                "duration": 320,
                                "pitch": 60,  # C4
                                "velocity": 100,
                                "lyric": "도"
                            },
                            {
                                "start": 320,
                                "duration": 320,
                                "pitch": 64,  # E4
                                "velocity": 90,
                                "lyric": "미"
                            },
                            {
                                "start": 640,
                                "duration": 320,
                                "pitch": 67,  # G4
                                "velocity": 95,
                                "lyric": "솔"
                            }
                        ],
                        "tempo": 120,
                        "timeSignature": {"numerator": 4, "denominator": 4},
                        "editMode": "select",
                        "snapSetting": "1/4",
                        "pixelsPerBeat": 80
                    }
                    piano_roll_features = PianoRoll(
                        height=600,
                        width=1000,
                        value=initial_value_features,
                        elem_id="piano_roll_features",  # 고유 ID 부여
                        use_backend_audio=True  # 백엔드 오디오 엔진 사용
                    )
            with gr.Row():
                with gr.Column():
                    btn_analyze_generated = gr.Button(
                        "🎶 노트에서 오디오 생성 & 분석",
                        variant="primary",
                        size="lg",
                        interactive=LIBROSA_AVAILABLE
                    )

            with gr.Row():
                with gr.Column():
                    btn_analyze_uploaded = gr.Button(
                        "📤 업로드된 오디오 분석",
                        variant="secondary",
                        size="lg",
                        interactive=LIBROSA_AVAILABLE
                    )

            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 🎛️ 신디사이저 설정")

                    # ADSR 설정
                    attack_features = gr.Slider(
                        minimum=0.001,
                        maximum=1.0,
                        value=0.01,
                        step=0.001,
                        label="Attack (초)"
                    )
                    decay_features = gr.Slider(
                        minimum=0.001,
                        maximum=1.0,
                        value=0.1,
                        step=0.001,
                        label="Decay (초)"
                    )
                    sustain_features = gr.Slider(
                        minimum=0.0,
                        maximum=1.0,
                        value=0.7,
                        step=0.01,
                        label="Sustain (레벨)"
                    )
                    release_features = gr.Slider(
                        minimum=0.001,
                        maximum=2.0,
                        value=0.3,
                        step=0.001,
                        label="Release (초)"
                    )

                    # 파형 설정
                    wave_type_features = gr.Dropdown(
                        choices=[
                            ("복합 파형 (Complex)", "complex"),
                            ("하모닉 합성 (Harmonic)", "harmonic"),
                            ("FM 합성 (FM)", "fm"),
                            ("톱니파 (Sawtooth)", "sawtooth"),
                            ("사각파 (Square)", "square"),
                            ("삼각파 (Triangle)", "triangle"),
                            ("사인파 (Sine)", "sine")
                        ],
                        value="complex",
                        label="파형 타입"
                    )
                with gr.Column():
                    gr.Markdown("### 📊 분석 설정")

                    # 분석할 특성 선택
                    include_f0_features = gr.Checkbox(
                        label="F0 (기본 주파수) 분석",
                        value=True
                    )
                    include_loudness_features = gr.Checkbox(
                        label="Loudness (음량) 분석",
                        value=True
                    )
                    include_voicing_features = gr.Checkbox(
                        label="Voice/Unvoice (유성음/무성음) 분석",
                        value=True
                    )

                    # F0 분석 방법
                    f0_method_features = gr.Dropdown(
                        choices=[
                            ("PYIN (정확함, 느림)", "pyin"),
                            ("PipTrack (빠름, 덜 정확)", "piptrack")
                        ],
                        value="pyin",
                        label="F0 추출 방법"
                    )

                    # Loudness 설정
                    loudness_use_db_features = gr.Checkbox(
                        label="Loudness를 dB 단위로 표시",
                        value=True
                    )
                    with gr.Row():
                        loudness_y_min_features = gr.Number(
                            label="Loudness 최소값 (비워두면 자동)",
                            value=None
                        )
                        loudness_y_max_features = gr.Number(
                            label="Loudness 최대값 (비워두면 자동)",
                            value=None
                        )

                    # Voice/Unvoice 설정
                    voicing_use_probs_features = gr.Checkbox(
                        label="Voice/Unvoice를 확률값으로 표시",
                        value=True,
                        info="체크 해제 시 이진값(0/1)으로 표시"
                    )
                with gr.Column():
                    gr.Markdown("### 🎤 오디오 업로드")
                    audio_upload_features = gr.Audio(
                        label="직접 분석할 오디오 파일",
                        type="filepath",
                        interactive=True
                    )

                    btn_generate_feature_demo = gr.Button(
                        "🎵 특성 분석용 데모 오디오 생성",
                        variant="secondary"
                    )
                    gr.Markdown("📄 F0 변화와 loudness 변화를 모두 포함하는 테스트 오디오를 생성합니다.")

            with gr.Row():
                with gr.Column():
                    features_status_text = gr.Textbox(
                        label="분석 상태",
                        interactive=False,
                        lines=4
                    )

            with gr.Row():
                with gr.Column():
                    # 비교용 오디오 재생
                    reference_audio_features = gr.Audio(
                        label="분석된 오디오 (참고용)",
                        type="filepath",
                        interactive=False
                    )

            with gr.Row():
                with gr.Column():
                    output_json_features = gr.JSON(label="오디오 특성 분석 결과")

            # 오디오 특성 분석 탭 이벤트 처리

            # 생성된 오디오 분석 버튼
            btn_analyze_generated.click(
                fn=synthesize_and_analyze_features,
                inputs=[
                    piano_roll_features,
                    attack_features,
                    decay_features,
                    sustain_features,
                    release_features,
                    wave_type_features,
                    include_f0_features,
                    include_loudness_features,
                    include_voicing_features,
                    f0_method_features,
                    loudness_y_min_features,
                    loudness_y_max_features,
                    loudness_use_db_features,
                    voicing_use_probs_features
                ],
                outputs=[piano_roll_features, features_status_text, reference_audio_features],
                show_progress=True
            )

            # 업로드된 오디오 분석 버튼
            btn_analyze_uploaded.click(
                fn=analyze_uploaded_audio_features,
                inputs=[
                    piano_roll_features,
                    audio_upload_features,
                    include_f0_features,
                    include_loudness_features,
                    include_voicing_features,
                    f0_method_features,
                    loudness_y_min_features,
                    loudness_y_max_features,
                    loudness_use_db_features,
                    voicing_use_probs_features
                ],
                outputs=[piano_roll_features, features_status_text, reference_audio_features],
                show_progress=True
            )

            # 데모 오디오 생성 및 분석 버튼
            def create_and_analyze_feature_demo():
                """특성 분석용 데모 오디오를 생성하고 자동으로 분석을 수행합니다."""
                demo_audio_path = generate_feature_demo_audio()
                if demo_audio_path:
                    # 초기 피아노롤 데이터
                    initial_piano_roll = {
                        "notes": [],
                        "tempo": 120,
                        "timeSignature": {"numerator": 4, "denominator": 4},
                        "editMode": "select",
                        "snapSetting": "1/4",
                        "pixelsPerBeat": 80
                    }

                                        # 오디오 특성 분석 수행 (F0, loudness, voice/unvoice 모두)
                    updated_piano_roll, status, _ = analyze_uploaded_audio_features(
                        initial_piano_roll, demo_audio_path,
                        include_f0=True, include_loudness=True, include_voicing=True, f0_method="pyin",
                        loudness_y_min=None, loudness_y_max=None, loudness_use_db=True, voicing_use_probs=True
                    )

                    return updated_piano_roll, status, demo_audio_path, demo_audio_path
                else:
                    return initial_value_features, "데모 오디오 생성에 실패했습니다.", None, None

            btn_generate_feature_demo.click(
                fn=create_and_analyze_feature_demo,
                outputs=[piano_roll_features, features_status_text, audio_upload_features, reference_audio_features],
                show_progress=True
            )

            # 노트 변경 시 JSON 출력 업데이트
            def update_features_json_output(piano_roll_data):
                return piano_roll_data

            piano_roll_features.change(
                fn=update_features_json_output,
                inputs=[piano_roll_features],
                outputs=[output_json_features],
                show_progress=False
            )

            # 재생 이벤트 로깅
            def log_features_play_event(event_data=None):
                print("🔊 Features Play event triggered:", event_data)
                return f"재생 시작: {event_data if event_data else '재생 중'}"

            def log_features_pause_event(event_data=None):
                print("🔊 Features Pause event triggered:", event_data)
                return f"일시정지: {event_data if event_data else '일시정지'}"

            def log_features_stop_event(event_data=None):
                print("🔊 Features Stop event triggered:", event_data)
                return f"정지: {event_data if event_data else '정지'}"

            piano_roll_features.play(log_features_play_event, outputs=features_status_text)
            piano_roll_features.pause(log_features_pause_event, outputs=features_status_text)
            piano_roll_features.stop(log_features_stop_event, outputs=features_status_text)

            if not LIBROSA_AVAILABLE:
                gr.Markdown("⚠️ librosa가 필요합니다")

if __name__ == "__main__":
    demo.launch()
