#!/usr/bin/env python3
"""
テストデバッグ用のヘルパースクリプト
このスクリプトは、テスト失敗時のデバッグを支援する機能を提供します。
"""

import argparse
import datetime
import logging
import os
import re
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
import pytest

@pytest.fixture
def debug_helper(tmp_path):
    """テストデバッグヘルパーのフィクスチャ"""
    log_dir = tmp_path / "test_logs"
    return TestDebugHelper(str(log_dir))

class TestDebugHelper:
    """テストデバッグを支援するクラス"""
    
    def setup_method(self, method):
        """各テストメソッド実行前の準備"""
        self.log_dir = Path("logs/test_debug")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """ロギングの設定"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"debug_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def test_run_tests(self):
        """run_tests メソッドのテスト"""
        log_file = self.run_tests(verbose=True)
        assert os.path.exists(log_file)
        
        # ログファイルの内容を確認
        with open(log_file) as f:
            content = f.read()
            assert "pytest" in content
    
    def test_analyze_test_failures(self):
        """analyze_test_failures メソッドのテスト"""
        # テスト失敗のサンプルログを作成
        log_content = """
        test_something FAILED
        Error: assertion failed
        
        test_another FAILED
        Exception: something went wrong
        """
        
        log_file = self.log_dir / "sample_failures.log"
        with open(log_file, "w") as f:
            f.write(log_content)
        
        failures = self.analyze_test_failures(str(log_file))
        assert "Error:" in failures
        assert "Exception:" in failures
    
    def test_create_debug_branch(self):
        """create_debug_branch メソッドのテスト"""
        bug_name = "test-bug"
        try:
            branch_name = self.create_debug_branch(bug_name)
            assert bug_name in branch_name
            assert "test-debug-" in branch_name
        except subprocess.CalledProcessError:
            pytest.skip("Git repository not available")
    
    def run_tests(self, test_path: Optional[str] = None, verbose: bool = True) -> str:
        """
        テストを実行し、結果をログファイルに保存
        
        Args:
            test_path: 実行するテストのパス（Noneの場合は全テスト実行）
            verbose: 詳細なログを出力するかどうか
        
        Returns:
            str: ログファイルのパス
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"test_run_{timestamp}.log"
        
        cmd = ["poetry", "run", "pytest"]
        if verbose:
            cmd.append("-v")
        if test_path:
            cmd.append(test_path)
        
        self.logger.info(f"テスト実行コマンド: {' '.join(cmd)}")
        
        with open(log_file, "w") as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            self.logger.error(f"テスト失敗: {result.stderr}")
        else:
            self.logger.info("テスト成功")
        
        return str(log_file)
    
    def analyze_test_failures(self, log_file: str) -> Dict[str, List[str]]:
        """
        テスト失敗のログを分析
        
        Args:
            log_file: 分析するログファイルのパス
        
        Returns:
            Dict[str, List[str]]: エラータイプごとの失敗したテストのリスト
        """
        failures: Dict[str, List[str]] = {}
        current_test = ""
        current_error = ""
        
        with open(log_file) as f:
            for line in f:
                # テスト名の検出
                test_match = re.match(r"^(test_.*?)\s", line)
                if test_match:
                    current_test = test_match.group(1)
                
                # エラータイプの検出
                error_match = re.search(r"(Error|Exception|Failure):", line)
                if error_match:
                    current_error = error_match.group(0)
                    if current_error not in failures:
                        failures[current_error] = []
                    if current_test:
                        failures[current_error].append(current_test)
        
        return failures
    
    def create_debug_branch(self, bug_name: str) -> str:
        """
        デバッグ用のGitブランチを作成
        
        Args:
            bug_name: バグの名前
        
        Returns:
            str: 作成したブランチ名
        """
        date = datetime.datetime.now().strftime("%Y%m%d")
        branch_name = f"test-debug-{bug_name}-{date}"
        
        try:
            subprocess.run(["git", "checkout", "-b", branch_name], check=True)
            self.logger.info(f"ブランチ作成成功: {branch_name}")
            return branch_name
        except subprocess.CalledProcessError as e:
            self.logger.error(f"ブランチ作成失敗: {e}")
            raise

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="テストデバッグヘルパー")
    parser.add_argument("--test-path", help="実行するテストのパス")
    parser.add_argument("--bug-name", help="バグの名前（ブランチ作成時に使用）")
    parser.add_argument("--verbose", "-v", action="store_true", help="詳細なログを出力")
    
    args = parser.parse_args()
    
    helper = TestDebugHelper()
    
    if args.bug_name:
        branch = helper.create_debug_branch(args.bug_name)
        print(f"Created debug branch: {branch}")
    
    log_file = helper.run_tests(args.test_path, args.verbose)
    failures = helper.analyze_test_failures(log_file)
    
    if failures:
        print("\nTest Failures Analysis:")
        for error_type, tests in failures.items():
            print(f"\n{error_type}")
            for test in tests:
                print(f"  - {test}")
    else:
        print("\nNo test failures found.")

if __name__ == "__main__":
    main() 