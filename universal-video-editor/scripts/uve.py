#!/usr/bin/env python3
"""Universal Video Editor command-line toolkit."""
import argparse, json, os, shutil, subprocess, sys, math, re
from pathlib import Path

VIDEO_EXTS = {".mp4",".mov",".mkv",".webm",".avi",".m4v"}
ROOT = Path(__file__).resolve().parents[1]

def fail(msg):
    print("ERROR:", msg, file=sys.stderr); raise SystemExit(2)

def run(cmd, capture=False):
    try:
        p = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE if capture else None,
                           stderr=subprocess.PIPE if capture else None)
        return p.stdout if capture else ""
    except FileNotFoundError:
        fail(f"Required executable not found: {cmd[0]}")
    except subprocess.CalledProcessError as e:
        fail((e.stderr or str(e))[-4000:])

def ffprobe(path):
    p = run(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(path)], True)
    return json.loads(p)

def duration(meta):
    try: return float(meta["format"]["duration"])
    except Exception: return 0.0

def cmd_doctor(_):
    for tool in ("ffmpeg","ffprobe"):
        print(f"{tool}: {shutil.which(tool) or 'MISSING'}")
    print(f"Python: {sys.version.split()[0]}")
    try:
        import PIL
        print(f"Pillow: {PIL.__version__}")
    except Exception: print("Pillow: not installed (contact sheets need Pillow)")
    try:
        import faster_whisper
        print("faster-whisper: installed")
    except Exception: print("faster-whisper: not installed (optional)")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"): raise SystemExit(1)

def cmd_setup(_):
    missing = [x for x in ("ffmpeg","ffprobe") if not shutil.which(x)]
    if missing:
        print("Install FFmpeg using the official package for your OS, add it to PATH, then rerun setup.")
        print("Missing:", ", ".join(missing)); raise SystemExit(1)
    try:
        import PIL
    except Exception:
        print("Install optional contact-sheet dependency: python -m pip install Pillow")
    print("READY — FFmpeg and ffprobe detected.")

def cmd_probe(a):
    m=ffprobe(a.input)
    out={"file":str(Path(a.input).resolve()),"duration_seconds":duration(m),"format":m.get("format",{}).get("format_name")}
    out["streams"]=[{"type":s.get("codec_type"),"codec":s.get("codec_name"),"width":s.get("width"),"height":s.get("height"),"fps":s.get("r_frame_rate"),"sample_rate":s.get("sample_rate")} for s in m.get("streams",[])]
    print(json.dumps(out,indent=2))

def cmd_inventory(a):
    folder=Path(a.folder)
    if not folder.is_dir(): fail("Folder does not exist.")
    items=[]
    for p in sorted(folder.rglob("*")):
        if p.suffix.lower() in VIDEO_EXTS:
            try:
                m=ffprobe(p); items.append({"file":str(p.resolve()),"duration_seconds":round(duration(m),2),"streams":[{"type":s.get("codec_type"),"width":s.get("width"),"height":s.get("height")} for s in m.get("streams",[])]})
            except SystemExit: print("Skipping unreadable file:",p)
    print(json.dumps(items,indent=2))

def cmd_init(a):
    out=Path(a.out).resolve()
    (out/"media").mkdir(parents=True,exist_ok=True); (out/"exports").mkdir(exist_ok=True); (out/"previews").mkdir(exist_ok=True)
    template=json.loads((ROOT/"templates/edit.example.json").read_text(encoding="utf-8"))
    template["name"]=a.name; template["clips"]=[]
    (out/"edit.json").write_text(json.dumps(template,indent=2),encoding="utf-8")
    (out/"README.txt").write_text("Place or reference source media in media/. Edit edit.json or ask your AI agent to build the timeline.\n",encoding="utf-8")
    print("Created project:",out)

def cmd_contact(a):
    try: from PIL import Image, ImageDraw
    except ImportError: fail("Pillow required. Run: python -m pip install Pillow")
    meta=ffprobe(a.input); dur=duration(meta)
    if dur<=0: fail("Could not determine media duration.")
    count=max(1,a.count); times=[dur*(i+0.5)/count for i in range(count)]
    thumbs=[]
    for t in times:
        raw=subprocess.run(["ffmpeg","-v","error","-ss",str(t),"-i",a.input,"-frames:v","1","-vf","scale=480:270:force_original_aspect_ratio=decrease,pad=480:270:(ow-iw)/2:(oh-ih)/2","-f","image2pipe","-vcodec","mjpeg","-"],stdout=subprocess.PIPE,check=True).stdout
        import io
        im=Image.open(io.BytesIO(raw)).convert("RGB")
        thumbs.append((t,im))
    cols=min(3,count); rows=math.ceil(count/cols); cellw,cellh=480,300
    sheet=Image.new("RGB",(cols*cellw,rows*cellh),(22,22,24)); d=ImageDraw.Draw(sheet)
    for i,(t,im) in enumerate(thumbs):
        x=(i%cols)*cellw; y=(i//cols)*cellh
        sheet.paste(im,(x,y)); d.text((x+10,y+276),f"{int(t//60):02}:{t%60:05.2f}",fill="white")
    dest=Path(a.out); dest.parent.mkdir(parents=True,exist_ok=True); sheet.save(dest)
    print("Saved contact sheet:",dest.resolve())

def esc_filter(s):
    return str(s).replace("\\","\\\\").replace(":","\\:").replace("'","\\'").replace("%","\\%").replace(",","\\,")

def cmd_render(a):
    plan_path=Path(a.plan).resolve()
    if not plan_path.exists(): fail("Edit plan not found.")
    plan=json.loads(plan_path.read_text(encoding="utf-8"))
    clips=plan.get("clips",[])
    if not clips: fail("edit.json has no clips. Add at least one clip.")
    out=Path(a.out).resolve(); out.parent.mkdir(parents=True,exist_ok=True)
    w=int(plan.get("output",{}).get("width",1920)); h=int(plan.get("output",{}).get("height",1080))
    fps=int(plan.get("output",{}).get("fps",30)); crf=str(plan.get("output",{}).get("crf",20)); preset=str(plan.get("output",{}).get("preset","medium"))
    inputs=[]; filters=[]; concat=[]
    for i,c in enumerate(clips):
        src=Path(c["src"])
        if not src.is_absolute(): src=(plan_path.parent/src).resolve()
        if not src.exists(): fail(f"Source file not found: {src}")
        meta=ffprobe(src); dur=duration(meta)
        start=float(c.get("start",0)); end=float(c.get("end",dur))
        if start<0 or end<=start or end>dur+0.05: fail(f"Invalid clip range {start}-{end} for {src} (duration {dur:.2f}s)")
        speed=float(c.get("speed",1.0))
        if speed<=0 or speed>8: fail("Clip speed must be >0 and <=8.")
        inputs += ["-i",str(src)]
        fit=c.get("fit","cover")
        if fit=="contain":
            vf=f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2"
        else:
            vf=f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"
        chain=f"[{i}:v]trim=start={start}:end={end},setpts=(PTS-STARTPTS)/{speed},fps={fps},{vf},setsar=1"
        fade_in=float(c.get("fade_in",0)); fade_out=float(c.get("fade_out",0))
        clipdur=(end-start)/speed
        if fade_in>0: chain+=f",fade=t=in:st=0:d={fade_in}"
        if fade_out>0: chain+=f",fade=t=out:st={max(0,clipdur-fade_out)}:d={fade_out}"
        filters.append(chain+f"[v{i}]"); concat.append(f"[v{i}]")
        # Keep source audio aligned with speed; optional source_gain.
        has_audio=any(s.get("codec_type")=="audio" for s in meta.get("streams",[]))
        if has_audio:
            atempo=[]
            rem=speed
            while rem>2: atempo.append("atempo=2"); rem/=2
            while rem<0.5: atempo.append("atempo=0.5"); rem/=0.5
            atempo.append(f"atempo={rem:.6f}")
            filters.append(f"[{i}:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS,{','.join(atempo)},volume={float(c.get('audio_gain',1.0))}[a{i}]")
        else:
            filters.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={clipdur}[a{i}]")
    filters.append("".join(concat)+f"concat=n={len(clips)}:v=1:a=0[vcat]")
    filters.append("".join(f"[a{i}]" for i in range(len(clips)))+f"concat=n={len(clips)}:v=0:a=1[acat]")
    look=plan.get("look",{})
    vf=[]
    if float(look.get("brightness",0))!=0: vf.append(f"eq=brightness={float(look['brightness'])}")
    if float(look.get("contrast",1))!=1 or float(look.get("saturation",1))!=1:
        vf.append(f"eq=contrast={float(look.get('contrast',1))}:saturation={float(look.get('saturation',1))}")
    if vf: filters.append("[vcat]"+",".join(vf)+"[vlook]"); vbase="[vlook]"
    else: vbase="[vcat]"
    # Titles: drawtext is intentionally simple and predictable; custom animated compositions can be supplied as overlay assets.
    titles=plan.get("titles",[])
    for j,t in enumerate(titles):
        text=esc_filter(t.get("text",""))
        start=float(t.get("start",0)); end=start+float(t.get("duration",3))
        size=int(t.get("font_size",56)); color=t.get("color","white")
        pos=t.get("position","center")
        y={"top":"h*0.12","center":"(h-text_h)/2","bottom":"h*0.82-text_h"}.get(pos,"(h-text_h)/2")
        font=t.get("fontfile")
        fontpart=f":fontfile='{esc_filter(font)}'" if font else ""
        box=":box=1:boxcolor=black@0.45:boxborderw=18" if t.get("box",False) else ""
        nxt=f"[vt{j}]"; filters.append(f"{vbase}drawtext=text='{text}'{fontpart}:fontsize={size}:fontcolor={color}:x=(w-text_w)/2:y={y}:enable='between(t,{start},{end})'{box}{nxt}"); vbase=nxt
    captions=plan.get("captions")
    if captions:
        cap=Path(captions)
        if not cap.is_absolute(): cap=(plan_path.parent/cap).resolve()
        if not cap.exists(): fail(f"Caption file not found: {cap}")
        filters.append(f"{vbase}subtitles='{esc_filter(str(cap))}'[vfinal]"); vbase="[vfinal]"
    audio=plan.get("audio",{})
    music=audio.get("music")
    if music:
        mp=Path(music)
        if not mp.is_absolute(): mp=(plan_path.parent/mp).resolve()
        if not mp.exists(): fail(f"Music file not found: {mp}")
        inputs += ["-stream_loop","-1","-i",str(mp)]
        mi=len([x for x in inputs if x=="-i"]) - 1
        total_duration = sum((float(c.get("end", 0)) - float(c.get("start", 0))) / float(c.get("speed", 1)) for c in clips)
        filters.append(f"[{mi}:a]volume={float(audio.get('music_gain',0.12))},atrim=duration={total_duration}[music]")
        filters.append(f"[acat][music]amix=inputs=2:duration=first:normalize=0[amix]")
        abase="[amix]"
    else: abase="[acat]"
    if audio.get("normalize",True):
        filters.append(f"{abase}loudnorm=I=-14:TP=-1.5:LRA=11[afinal]"); abase="[afinal]"
    graph=";".join(filters)
    cmd=["ffmpeg","-y","-hide_banner","-loglevel","warning"]+inputs+["-filter_complex",graph,"-map",vbase,"-map",abase,"-r",str(fps),"-c:v","libx264","-preset",preset,"-crf",crf,"-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-movflags","+faststart",str(out)]
    if a.preview: cmd[cmd.index("-crf")+1]="28"; cmd[cmd.index("-preset")+1]="ultrafast"
    run(cmd)
    if not out.exists() or out.stat().st_size==0: fail("Render did not produce an output file.")
    print("Rendered:",out,"(",out.stat().st_size,"bytes )")

def cmd_validate(a):
    m=ffprobe(a.input); d=duration(m)
    if d<=0: fail("Output duration is missing or zero.")
    streams=m.get("streams",[])
    if not any(s.get("codec_type")=="video" for s in streams): fail("No video stream found.")
    if not any(s.get("codec_type")=="audio" for s in streams): print("WARNING: output has no audio stream.")
    v=next(s for s in streams if s.get("codec_type")=="video")
    print(json.dumps({"valid":True,"duration_seconds":round(d,3),"width":v.get("width"),"height":v.get("height"),"video_codec":v.get("codec_name"),"audio":any(s.get("codec_type")=="audio" for s in streams),"size_bytes":Path(a.input).stat().st_size},indent=2))

def cmd_transcribe(a):
    try: from faster_whisper import WhisperModel
    except ImportError: fail("Install optional dependency: python -m pip install faster-whisper")
    model=WhisperModel(a.model,device="auto",compute_type="int8")
    segs,info=model.transcribe(a.input,word_timestamps=True)
    result={"language":info.language,"segments":[]}
    for s in segs:
        result["segments"].append({"start":s.start,"end":s.end,"text":s.text,"words":[{"start":w.start,"end":w.end,"word":w.word} for w in (s.words or [])]})
    Path(a.out).write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    print("Transcript saved:",Path(a.out).resolve())

def main():
    p=argparse.ArgumentParser(description="Universal Video Editor toolkit")
    sub=p.add_subparsers(dest="cmd",required=True)
    for name,fn in [("doctor",cmd_doctor),("setup",cmd_setup)]:
        q=sub.add_parser(name); q.set_defaults(func=fn)
    q=sub.add_parser("probe"); q.add_argument("input"); q.set_defaults(func=cmd_probe)
    q=sub.add_parser("inventory"); q.add_argument("folder"); q.set_defaults(func=cmd_inventory)
    q=sub.add_parser("init"); q.add_argument("name"); q.add_argument("--out",default="uve-project"); q.set_defaults(func=cmd_init)
    q=sub.add_parser("contact-sheet"); q.add_argument("input"); q.add_argument("--out",default="contact.jpg"); q.add_argument("--count",type=int,default=9); q.set_defaults(func=cmd_contact)
    q=sub.add_parser("render"); q.add_argument("plan"); q.add_argument("--out",default="final.mp4"); q.add_argument("--preview",action="store_true"); q.set_defaults(func=cmd_render)
    q=sub.add_parser("validate"); q.add_argument("input"); q.set_defaults(func=cmd_validate)
    q=sub.add_parser("transcribe"); q.add_argument("input"); q.add_argument("--out",default="transcript.json"); q.add_argument("--model",default="small"); q.set_defaults(func=cmd_transcribe)
    a=p.parse_args(); a.func(a)

if __name__=="__main__": main()
