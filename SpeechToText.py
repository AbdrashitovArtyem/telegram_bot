import soundfile as sf
import speech_recognition as sr


def ogg2wav(ofn):
    wfn = ofn.replace('.ogg', '.wav')
    data, samplerate = sf.read(ofn)
    sf.write(wfn, data, samplerate)
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

