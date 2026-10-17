import sys, tempfile
sys.path.insert(0, "core")
from approval_flow import ApprovalQueue

def test_flow():
    with tempfile.TemporaryDirectory() as td:
        q = ApprovalQueue(td)
        pid, st = q.propose("s1", "click", {"selector": "#go"})
        assert st == "pending" and pid
        assert len(q.pending("s1")) == 1
        r = q.resolve(pid, True, resolved_by="human")
        assert r["status"] == "approved" and r["resolved_by"] == "human"
        assert q.pending("s1") == []
        pid2, st2 = q.propose("s1", "navigate", {"url": "https://x.com/signup"})
        assert st2 == "denied" and pid2 is None
        print("approval flow OK (incl. account-creation hard deny)")

if __name__ == "__main__":
    test_flow()
