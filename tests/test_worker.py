from unittest.mock import patch
import importlib.util, time, tempfile, pathlib, json, subprocess, unittest, threading, urllib.request, urllib.error, os, sys
spec=importlib.util.spec_from_file_location('worker',pathlib.Path(__file__).parents[1]/'worker.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
class MediaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();w.ROOT=pathlib.Path(cls.tmp.name);w.TOKEN='bayan-test-token-not-a-real-secret';w.OPENAI_KEY='';w.init_db()
        cls.source=w.ROOT/'assets'/'12345678-1234-1234-1234-123456789012'
        subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-f','lavfi','-i','color=c=0x102038:s=640x360:r=25:d=4','-f','lavfi','-i','sine=frequency=440:duration=4','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-shortest',str(cls.source)+'.mp4'],check=True)
        pathlib.Path(str(cls.source)+'.mp4').rename(cls.source)
        cls.server=w.ThreadingHTTPServer(('127.0.0.1',0),w.Handler);cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start();cls.base='http://127.0.0.1:'+str(cls.server.server_port)
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.tmp.cleanup()
    def test_1_captions(self):
        raw={'events':[{'tStartMs':0,'dDurationMs':2000,'segs':[{'utf8':'السلام عليكم'}]},{'tStartMs':1000,'dDurationMs':2000,'segs':[{'utf8':'السلام عليكم ورحمة الله'}]}]}
        s=w.parse_json3(raw,'p');self.assertEqual(len(s),2);self.assertEqual(s[1]['arabic_text'],'ورحمة الله');self.assertGreaterEqual(s[1]['start_time'],s[0]['end_time'])
        self.assertEqual(w.merge_fragments(s)[0]['arabic_text'],'السلام عليكم ورحمة الله')
    def test_2_missing_ai(self):
        seg=w.make_segment('p',0,2,'السلام عليكم');payload={'kind':'translate','project':{'id':'p','title':'QA','segments':[seg]}}
        job=w.new_job(payload);w.process_job(job['id'],payload);self.assertEqual(w.job_state(job['id'])['status'],'blocked')
    def test_3_real_ffmpeg(self):
        ass=(pathlib.Path(__file__).parent/'fixtures/captions.ass').read_text();payload={'kind':'export','project':{'id':'p','title':'QA','segments':[]},'asset':self.source.name,'ass':ass,'quality':'720'}
        job=w.new_job(payload);w.process_job(job['id'],payload);state=w.job_state(job['id']);self.assertEqual(state['status'],'complete',state.get('error'));self.assertGreater(state['result']['size'],10000)
        output=w.ROOT/job['id']/'export.mp4';meta=w.probe(output);self.assertEqual(meta['width'],640);self.assertEqual(meta['height'],360);self.assertAlmostEqual(meta['duration'],4,delta=.15)
        # Decode frames and ensure burned-in subtitle pixels actually differ.
        def frame(p):return subprocess.check_output(['ffmpeg','-v','error','-ss','1','-i',str(p),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'])
        self.assertNotEqual(frame(self.source),frame(output))
        dest=(w.ROOT/'render-test.mp4');dest.write_bytes(output.read_bytes())
        request=urllib.request.Request(self.base+'/jobs/'+job['id']+'/file',headers={'Authorization':'Bearer '+w.TOKEN,'Range':'bytes=0-99'})
        with urllib.request.urlopen(request) as r:self.assertEqual(r.status,206);self.assertEqual(len(r.read()),100)
    def test_4_auth_and_durability(self):
        with self.assertRaises(urllib.error.HTTPError) as e:urllib.request.urlopen(self.base+'/health')
        self.assertEqual(e.exception.code,401)
        req=urllib.request.Request(self.base+'/health',headers={'Authorization':'Bearer '+w.TOKEN})
        with urllib.request.urlopen(req) as r:self.assertTrue(json.load(r)['ffmpeg'])
        j=w.new_job({'kind':'translate','project':{'segments':[]}});w.update(j['id'],status='running');w.init_db();self.assertEqual(w.job_state(j['id'])['status'],'failed')
    def test_5_free_import_keeps_arabic(self):
        seg=w.make_segment('p',0,2,'السلام عليكم');payload={'kind':'import','project':{'id':'p','title':'QA','url':'https://youtu.be/abcdefghijk','segments':[]},'costPolicy':'free'}
        job=w.new_job(payload)
        with patch.object(w,'youtube_captions',return_value=([seg],{'duration':2})), patch.object(w,'translate',side_effect=AssertionError('must not call paid translation')):
            w.process_job(job['id'],payload)
        state=w.job_state(job['id']);self.assertEqual(state['status'],'complete',state.get('error'));self.assertEqual(state['result']['segments'][0]['arabic_text'],'السلام عليكم');self.assertEqual(state['result']['segments'][0]['french_text'],'')
    def test_6_paid_key_never_enables_free_job(self):
        seg=w.make_segment('p',0,2,'العلم نور');payload={'kind':'translate','project':{'id':'p','title':'QA','segments':[seg]},'costPolicy':'free'}
        job=w.new_job(payload)
        with patch.object(w,'OPENAI_KEY','a-key-must-not-be-used'),patch.object(w,'ALLOW_PAID_AI',True),patch.object(w,'api_request',side_effect=AssertionError('paid request forbidden')):
            w.process_job(job['id'],payload)
        self.assertEqual(w.job_state(job['id'])['status'],'blocked')
    def test_7_storage_limits_and_cleanup(self):
        with patch.object(w.shutil,'disk_usage',return_value=type('Usage',(),{'free':100})()):
            with self.assertRaises(ValueError):w.ensure_space(1000)
        old=w.ROOT/'assets'/'expired';old.write_bytes(b'old');os.utime(old,(0,0));w.cleanup_expired();self.assertFalse(old.exists());self.assertTrue(self.source.exists())
    def test_9_export_size_is_bounded(self):
        meta={'duration':180,'height':1080,'videoBitrate':3_800_000}
        rate=w.video_bitrate(meta,1080);self.assertLessEqual(rate,4_180_000);self.assertGreaterEqual(rate,1_500_000)
        self.assertLess(w.video_bitrate(meta,720),rate)
        long={'duration':3600,'height':1080,'videoBitrate':0}
        self.assertLessEqual(w.video_bitrate(long,1080)*3600/8,w.MAX_BYTES*2)
    def test_10_regeneration_replaces_previous_mp4(self):
        ass=(pathlib.Path(__file__).parent/'fixtures/captions.ass').read_text();payload={'kind':'export','project':{'id':'p','title':'QA','segments':[]},'asset':self.source.name,'ass':ass,'quality':'original'}
        first=w.new_job(payload);w.process_job(first['id'],payload);self.assertTrue((w.ROOT/first['id']/'export.mp4').exists())
        second=w.new_job(payload);w.process_job(second['id'],payload);self.assertEqual(w.job_state(second['id'])['status'],'complete')
        self.assertFalse((w.ROOT/first['id']/'export.mp4').exists());self.assertTrue((w.ROOT/second['id']/'export.mp4').exists())
    def test_12_ffmpeg_threads_follow_cpu_quota(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);(root/'cpu.max').write_text('200000 100000\n');self.assertEqual(w.cpu_quota(root),2)
            (root/'cpu.max').write_text('max 100000\n');self.assertEqual(w.cpu_quota(root),os.cpu_count())
        self.assertLessEqual(w.FFMPEG_THREADS,4)
    def test_13_low_space_evicts_unused_media_oldest_first(self):
        idle=w.new_job({'kind':'export','project':{'segments':[]},'asset':'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'});w.update(idle['id'],status='complete')
        busy=w.new_job({'kind':'export','project':{'segments':[]},'asset':'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'})
        old_asset=w.ROOT/'assets'/'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa';busy_asset=w.ROOT/'assets'/'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
        fresh=w.ROOT/'assets'/'cccccccc-cccc-cccc-cccc-cccccccccccc';(w.ROOT/idle['id']).mkdir(exist_ok=True);old_mp4=w.ROOT/idle['id']/'export.mp4'
        for f,age in ((old_asset,3600),(busy_asset,7200),(old_mp4,1800),(fresh,0)):f.write_bytes(b'x');os.utime(f,(time.time()-age,)*2)
        existing=lambda:sum(f.exists() for f in (old_asset,old_mp4))
        # Free space grows by one unit per evicted file; two units are needed.
        with patch.object(w.shutil,'disk_usage',side_effect=lambda _:type('Usage',(),{'free':w.RESERVE_BYTES+2-existing()})()):
            w.ensure_space(1);self.assertFalse(old_asset.exists());self.assertTrue(old_mp4.exists())
            w.ensure_space(2);self.assertFalse(old_mp4.exists())
            with self.assertRaises(ValueError):w.ensure_space(3)
        self.assertTrue(busy_asset.exists());self.assertTrue(fresh.exists())
        w.update(busy['id'],status='failed')
    def test_11_youtube_bot_check_is_actionable(self):
        class DownloadError(Exception):pass
        class FakeYDL:
            def __init__(self,*a):pass
            def __enter__(self):return self
            def __exit__(self,*a):return False
            def extract_info(self,*a,**k):raise DownloadError('ERROR: [youtube] yy_ABo1l80o: Sign in to confirm you’re not a bot. Use --cookies-from-browser or --cookies for the authentication.')
        fake=type(sys)('yt_dlp');fake.YoutubeDL=FakeYDL
        for kind in ('import','export'):
            payload={'kind':kind,'costPolicy':'free','ass':'[Script Info]\n','project':{'id':'p','title':'QA','url':'https://youtu.be/yy_ABo1l80o','segments':[]}}
            job=w.new_job(payload)
            with patch.dict(sys.modules,{'yt_dlp':fake}):w.process_job(job['id'],payload)
            state=w.job_state(job['id']);self.assertEqual(state['status'],'blocked',state.get('error'));self.assertIn('fichier vidéo original',state['error']);self.assertNotIn('ERROR:',state['error'])
    def test_8_youtube_guard(self):
        for url in ['http://localhost/admin','https://youtube.com.evil.test/watch?v=abcdefghijk','file:///etc/passwd']:
            with self.assertRaises(ValueError):w.valid_youtube(url)
if __name__=='__main__':unittest.main(verbosity=2)
