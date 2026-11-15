"""Sample sources for the try-it players (audio/try/*.mp3), so a visitor can hear the presets without a file of their own.

Taken from the owner's Splice packs (F:/Samples/Samples/packs). Each is 10 s (looped if the file is shorter), loudness-matched to
-18 LUFS (true peak -2 dB) and encoded at 160 kb/s. The player brings every source to the same peak before the engine.
    python tools/make_tryit_samples.py
"""
import os, subprocess

PACKS = "F:/Samples/Samples/packs/"
OUT = os.path.join(os.path.dirname(__file__), "..", "audio", "try")
SOURCES = {
    "guitar-riff": "Universal Pop and Vocals/Audentity_Records_-_Universal_Pop_&_Vocals_repack/loops/Instrumental_Loops/guitar_loops/AU_UPV_Answer_Guitar_Loop_98_Gmaj_Dry.wav",
    "guitar-line": "Guitar Addict/Guitar_Addict_-_Zenhiser/GUITARADDICT_-_Guitar_Lines_-_Dry/058_Guitar_Line__Dry__Amajor_128bpm_-_GUITARADDICT_Zenhiser.wav",
    "guitar-clean": "Ambient Cinematic Guitars 4/Epic_Stock_Media_-_Ambient_Cinematic_Guitars_4/Loops/90_Arpeggie_Jackson/Dry/ESM_ACGL4_90_guitar_electric_loop_arpeggie_jackson_dry_1_D.wav",
    "nylon": "Nylon Bossa Nova Guitar/Guitar_Loops/DIASPORA__nylon_guitar_loop_41_bossa_nova_120_bpm_Cmaj.wav",
    "bass": "Indie Nu Disco/Samplestar_-_Indie_Nu_Disco_-_Splice/Kit_04_Gold_110/SS_IND_110_bass_loop_kit04_gold_bass_d#_dry.wav",
    "synth-bass": "Tenchu 2/DopeBoyzMuzic_-_Tenchu_2/Loops/Bass_Loops/Bass_Synth_Loops/DBM_TC2_130_Bass_Synth_Loop_The_Gathering_Fmin.wav",
    "drums": "Organic Hip-Hop/TS_ORGANIC_HIP_HOP/loops/grooves/TS_ORGANIC_HIP_HOP_85_drum_loop_groove_hit_the_rim.wav",
    "rock-drums": "Travis Barker Drum Kit/TRAVIS_BARKER_sample_pack/TRAVIS_BARKER_drums/TRAVIS_BARKER_drum_loops/TRAVIS_BARKER_drum_loop_trash_155.wav",
    "synth-lead": "Day Dreaming 2 - Lo-Fi Hip-Hop Jamz/Origin_Sound_-_Day_Dreaming_2/Music_Loops/Melodics/OS_DD2_80_Am_Drowsy_Moog_Lead.wav",
    "wurlitzer": "Brax Stax Braxton Cook/Brax_Stax/Loops/Wurlitzer_Loops/SO_BRAX_90_wurlitzer_green_dry_Gb.wav",
    "rhodes": "Resampled Cinematic Soul/Loops/Rhodes/SO_RE_80_rhodes_high_pomelo_Abmaj.wav",
    "pad": "Chillwave/_for_Splice/Sample_Magic_-_Chillwave_-_Wavs/pads/pads_-_100bpm/cw_pad100_sombre_Eb.wav",
    "pluck": None,   # filled from the audition list below (path search), see find()
    "vocal": None,
    "cello": None,
    "sax": "Brax Stax Braxton Cook/Brax_Stax/Loops/Alto_Sax_Phrases/Sax_Solos/SO_BRAX_90_sax_solo_blush_Gb.wav",
    "flute": "Tenchu 2/DopeBoyzMuzic_-_Tenchu_2/Loops/Flute_Loops/DBM_TC2_87_Flute_High_Loop_Emperor_Bmin.wav",
}
BY_NAME = {"pluck": "OS_AS_100_Fm_Teal_Synth_Plucks.wav", "vocal": "GIO_MEV_90_vocal_dvir_cohen_bayat_breathy_verse_G.wav",
           "cello": "PL_SYM_140_Cello_Loop_High_Grief_Dm.wav"}


def find(name):
    for dp, _, fn in os.walk(PACKS):
        if name in fn: return os.path.join(dp, name)
    raise FileNotFoundError(name)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for key, rel in SOURCES.items():
        src = find(BY_NAME[key]) if rel is None else PACKS + rel
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-stream_loop", "-1", "-i", src, "-t", "10",
                        "-af", "loudnorm=I=-18:TP=-2,afade=t=in:d=0.01,afade=t=out:st=9.97:d=0.03", "-ar", "48000", "-b:a", "160k",
                        os.path.join(OUT, key + ".mp3")], check=True)
        print(key, "<-", os.path.basename(src))
