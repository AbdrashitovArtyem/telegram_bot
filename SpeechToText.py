import soundfile as sf
import speech_recognition as sr
import moviepy.editor as mp

def ogg2wav(ofn):
    if ofn.endswith('.ogg') or ofn.endswith('.oga'):
        wfn = ofn.rsplit('.', 1)[0] + '.wav'
        data, samplerate = sf.read(ofn)
        sf.write(wfn, data, samplerate)
    elif ofn.endswith('.mp4'):
        wfn = ofn.rsplit('.', 1)[0] + '.wav'
        video = mp.VideoFileClip(ofn)
        audio = video.audio
        audio.write_audiofile(wfn)
    else:
        wfn = ofn
    return wfn

def speech_to_text(filepath):
    filepath = ogg2wav(filepath)
    r = sr.Recognizer()
    with sr.AudioFile(filepath) as source:
        audio = r.record(source)

    try:
        return r.recognize_google(audio, language='ru-RU')
    except sr.UnknownValueError:
        return "Мне не удалось понять аудиозапись"
    except sr.RequestError as e:
        return "Ошибка {0}".format(e)
