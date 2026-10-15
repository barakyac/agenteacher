import threading
import unittest
from unittest.mock import patch
from orchestrator import OrchestratorAgent

class OrchestratorTests(unittest.TestCase):
    def test_workers_overlap(self):
        agent=OrchestratorAgent('test','test',[])
        barrier=threading.Barrier(2,timeout=2)
        def worker(): barrier.wait()
        with patch.object(agent,'conversation',worker),patch.object(agent,'coach',worker),patch.object(agent,'spelling',lambda: agent.emit('spelling','result',allowed=True,status='ok',hint='')):
            events=list(agent.run())
        self.assertFalse(any(e['type']=='error' for e in events))
        self.assertEqual({e['agent'] for e in events if e['type']=='done'},{'coach','conversation','spelling'})
        self.assertEqual(events[-1]['type'],'complete')

    def test_failure_isolated(self):
        agent=OrchestratorAgent('test','test',[])
        def conversation(): agent.emit('conversation','delta',text='Preserved answer')
        with patch.object(agent,'conversation',conversation),patch.object(agent,'coach',side_effect=ValueError('invalid JSON')),patch.object(agent,'spelling',lambda: agent.emit('spelling','result',allowed=True,status='ok',hint='')):
            events=list(agent.run())
        self.assertTrue(any(e.get('text')=='Preserved answer' for e in events))
        self.assertEqual([e['agent'] for e in events if e['type']=='error'],['coach'])
        self.assertEqual(events[-1]['type'],'complete')

    def test_language_block_suppresses_conversation(self):
        agent=OrchestratorAgent('test','test',[])
        with patch.object(agent,'conversation',lambda: agent.emit('conversation','delta',text='hidden')),patch.object(agent,'coach',lambda: None),patch.object(agent,'spelling',lambda: agent.emit('spelling','result',allowed=False,status='blocked',hint='blocked')):
            events=list(agent.run())
        self.assertFalse(any(e['type']=='delta' for e in events))
        self.assertEqual(events[-1]['type'],'blocked')

    def test_scripts(self):
        from language_guard import validate_script
        validate_script('שלום English 123 😊 שָׁלוֹם')
        for text in ['hello привет','مرحبا','你好','bonjour café']:
            with self.assertRaises(ValueError): validate_script(text)

if __name__=='__main__': unittest.main()
