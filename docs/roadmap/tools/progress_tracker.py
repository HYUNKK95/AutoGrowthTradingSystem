#!/usr/bin/env python3
"""
📊 로드맵 진행률 추적기 (Roadmap Progress Tracker)

이 스크립트는 AutoGrowthTradingSystem의 로드맵 진행률을 추적하고 분석합니다.
"""

import os
import re
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import yaml

class RoadmapProgressTracker:
    def __init__(self, roadmap_dir: str = "docs/roadmap"):
        self.roadmap_dir = Path(roadmap_dir)
        self.phases = {}
        self.tasks = {}
        self.milestones = {}
        self.progress_data = {}
        
    def load_roadmap_files(self):
        """로드맵 파일들을 로드합니다."""
        print("📁 로드맵 파일 로딩 중...")
        
        # Phase 파일들 로드
        phase_files = list(self.roadmap_dir.glob("PHASE_*.md"))
        for phase_file in phase_files:
            self.load_phase_file(phase_file)
        
        # 메인 로드맵 파일 로드
        main_roadmap = self.roadmap_dir / "MAIN_ROADMAP.md"
        if main_roadmap.exists():
            self.load_main_roadmap(main_roadmap)
        
        print(f"✅ {len(self.phases)} 개의 Phase 로드 완료")
    
    def load_phase_file(self, phase_file: Path):
        """Phase 파일을 로드합니다."""
        try:
            with open(phase_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Phase 정보 추출
            phase_info = self.extract_phase_info(content, phase_file.name)
            if phase_info:
                self.phases[phase_info['id']] = phase_info
                
                # 작업들 추출
                tasks = self.extract_tasks(content, phase_info['id'])
                self.tasks.update(tasks)
                
        except Exception as e:
            print(f"❌ {phase_file.name} 로드 실패: {e}")
    
    def extract_phase_info(self, content: str, filename: str) -> Optional[Dict]:
        """Phase 정보를 추출합니다."""
        # Phase ID 추출
        phase_match = re.search(r'Phase (\d+(?:\.\d+)?)', content)
        if not phase_match:
            return None
        
        phase_id = phase_match.group(1)
        
        # Phase 제목 추출
        title_match = re.search(r'# .*?Phase \d+(?:\.\d+)?: (.+?)(?:\n|$)', content)
        title = title_match.group(1) if title_match else f"Phase {phase_id}"
        
        # 기간 추출
        duration_match = re.search(r'기간.*?(\d+)-(\d+)일', content)
        duration = {
            'min': int(duration_match.group(1)) if duration_match else 0,
            'max': int(duration_match.group(2)) if duration_match else 0
        }
        
        # 예산 추출
        budget_match = re.search(r'예산.*?\$([\d,]+)', content)
        budget = int(budget_match.group(1).replace(',', '')) if budget_match else 0
        
        return {
            'id': phase_id,
            'title': title,
            'filename': filename,
            'duration': duration,
            'budget': budget,
            'status': 'planned'  # 기본값
        }
    
    def extract_tasks(self, content: str, phase_id: str) -> Dict:
        """작업들을 추출합니다."""
        tasks = {}
        
        # 체크리스트 패턴 찾기
        checklist_pattern = r'- \[([ x])\] (.+?)(?: \((\d+(?:\.\d+)?)일\))?(?: \(완료: (\d{4}-\d{2}-\d{2})\))?'
        matches = re.finditer(checklist_pattern, content, re.MULTILINE)
        
        task_id = 1
        for match in matches:
            is_completed = match.group(1) == 'x'
            task_name = match.group(2).strip()
            duration = float(match.group(3)) if match.group(3) else 0
            completion_date = match.group(4) if match.group(4) else None
            
            task_key = f"{phase_id}.{task_id}"
            tasks[task_key] = {
                'id': task_key,
                'phase_id': phase_id,
                'name': task_name,
                'duration': duration,
                'completed': is_completed,
                'completion_date': completion_date,
                'status': 'completed' if is_completed else 'pending'
            }
            task_id += 1
        
        return tasks
    
    def load_main_roadmap(self, main_roadmap: Path):
        """메인 로드맵 파일을 로드합니다."""
        try:
            with open(main_roadmap, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 전체 진행률 정보 추출
            progress_match = re.search(r'전체 진행률.*?(\d+)%', content)
            if progress_match:
                self.progress_data['overall'] = int(progress_match.group(1))
                
        except Exception as e:
            print(f"❌ 메인 로드맵 로드 실패: {e}")
    
    def calculate_phase_progress(self, phase_id: str) -> Dict:
        """Phase별 진행률을 계산합니다."""
        phase_tasks = [task for task in self.tasks.values() if task['phase_id'] == phase_id]
        
        if not phase_tasks:
            return {'completed': 0, 'total': 0, 'percentage': 0}
        
        completed_tasks = [task for task in phase_tasks if task['completed']]
        total_duration = sum(task['duration'] for task in phase_tasks)
        completed_duration = sum(task['duration'] for task in completed_tasks)
        
        return {
            'completed': len(completed_tasks),
            'total': len(phase_tasks),
            'percentage': round((len(completed_tasks) / len(phase_tasks)) * 100, 1),
            'duration_completed': completed_duration,
            'duration_total': total_duration,
            'duration_percentage': round((completed_duration / total_duration) * 100, 1) if total_duration > 0 else 0
        }
    
    def calculate_overall_progress(self) -> Dict:
        """전체 진행률을 계산합니다."""
        total_tasks = len(self.tasks)
        completed_tasks = len([task for task in self.tasks.values() if task['completed']])
        
        total_duration = sum(task['duration'] for task in self.tasks.values())
        completed_duration = sum(task['duration'] for task in self.tasks.values() if task['completed'])
        
        return {
            'completed_tasks': completed_tasks,
            'total_tasks': total_tasks,
            'percentage': round((completed_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0,
            'duration_completed': completed_duration,
            'duration_total': total_duration,
            'duration_percentage': round((completed_duration / total_duration) * 100, 1) if total_duration > 0 else 0
        }
    
    def generate_progress_report(self) -> str:
        """진행률 보고서를 생성합니다."""
        report = []
        report.append("# 📊 로드맵 진행률 보고서")
        report.append(f"생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 전체 진행률
        overall_progress = self.calculate_overall_progress()
        report.append("## 🎯 전체 진행률")
        report.append(f"- **완료된 작업**: {overall_progress['completed_tasks']}/{overall_progress['total_tasks']}")
        report.append(f"- **진행률**: {overall_progress['percentage']}%")
        report.append(f"- **완료된 기간**: {overall_progress['duration_completed']:.1f}/{overall_progress['duration_total']:.1f}일")
        report.append(f"- **기간 진행률**: {overall_progress['duration_percentage']}%")
        report.append("")
        
        # Phase별 진행률
        report.append("## 📋 Phase별 진행률")
        for phase_id in sorted(self.phases.keys(), key=lambda x: float(x)):
            phase = self.phases[phase_id]
            progress = self.calculate_phase_progress(phase_id)
            
            status_emoji = "✅" if progress['percentage'] == 100 else "🔄" if progress['percentage'] > 0 else "⏳"
            
            report.append(f"### {status_emoji} Phase {phase_id}: {phase['title']}")
            report.append(f"- **진행률**: {progress['percentage']}% ({progress['completed']}/{progress['total']})")
            report.append(f"- **기간**: {progress['duration_completed']:.1f}/{progress['duration_total']:.1f}일")
            report.append(f"- **예산**: ${phase['budget']:,}")
            report.append("")
        
        # 최근 완료된 작업
        recent_completed = self.get_recent_completed_tasks()
        if recent_completed:
            report.append("## ✅ 최근 완료된 작업")
            for task in recent_completed[:10]:  # 최근 10개만
                report.append(f"- **{task['phase_id']}**: {task['name']} (완료: {task['completion_date']})")
            report.append("")
        
        # 진행 중인 작업
        in_progress = self.get_in_progress_tasks()
        if in_progress:
            report.append("## 🔄 진행 중인 작업")
            for task in in_progress[:10]:  # 최근 10개만
                report.append(f"- **{task['phase_id']}**: {task['name']} ({task['duration']}일)")
            report.append("")
        
        # 지연된 작업
        delayed_tasks = self.get_delayed_tasks()
        if delayed_tasks:
            report.append("## ⚠️ 지연된 작업")
            for task in delayed_tasks:
                report.append(f"- **{task['phase_id']}**: {task['name']} (예정: {task['estimated_completion']})")
            report.append("")
        
        return "\n".join(report)
    
    def get_recent_completed_tasks(self) -> List[Dict]:
        """최근 완료된 작업들을 반환합니다."""
        completed_tasks = [task for task in self.tasks.values() if task['completed'] and task['completion_date']]
        
        # 완료일 기준으로 정렬
        completed_tasks.sort(key=lambda x: x['completion_date'], reverse=True)
        return completed_tasks
    
    def get_in_progress_tasks(self) -> List[Dict]:
        """진행 중인 작업들을 반환합니다."""
        # 완료되지 않은 작업 중에서 진행 중인 것으로 추정되는 작업들
        in_progress = []
        for task in self.tasks.values():
            if not task['completed'] and task['duration'] > 0:
                in_progress.append(task)
        
        return in_progress
    
    def get_delayed_tasks(self) -> List[Dict]:
        """지연된 작업들을 반환합니다."""
        # 현재 날짜 기준으로 예상 완료일이 지난 작업들
        delayed_tasks = []
        current_date = datetime.now()
        
        for task in self.tasks.values():
            if not task['completed'] and task['duration'] > 0:
                # 간단한 지연 계산 (실제로는 더 복잡한 로직 필요)
                estimated_completion = current_date + timedelta(days=task['duration'])
                if estimated_completion < current_date:
                    task['estimated_completion'] = estimated_completion.strftime('%Y-%m-%d')
                    delayed_tasks.append(task)
        
        return delayed_tasks
    
    def export_to_json(self, output_file: str = "roadmap_progress.json"):
        """진행률 데이터를 JSON으로 내보냅니다."""
        data = {
            'generated_at': datetime.now().isoformat(),
            'phases': self.phases,
            'tasks': self.tasks,
            'overall_progress': self.calculate_overall_progress(),
            'phase_progress': {
                phase_id: self.calculate_phase_progress(phase_id)
                for phase_id in self.phases.keys()
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON 파일 저장 완료: {output_file}")
    
    def export_to_yaml(self, output_file: str = "roadmap_progress.yaml"):
        """진행률 데이터를 YAML로 내보냅니다."""
        data = {
            'generated_at': datetime.now().isoformat(),
            'phases': self.phases,
            'tasks': self.tasks,
            'overall_progress': self.calculate_overall_progress(),
            'phase_progress': {
                phase_id: self.calculate_phase_progress(phase_id)
                for phase_id in self.phases.keys()
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        
        print(f"✅ YAML 파일 저장 완료: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='로드맵 진행률 추적기')
    parser.add_argument('--roadmap-dir', default='docs/roadmap', help='로드맵 디렉토리 경로')
    parser.add_argument('--output', default='roadmap_progress_report.md', help='출력 파일명')
    parser.add_argument('--format', choices=['markdown', 'json', 'yaml'], default='markdown', help='출력 형식')
    parser.add_argument('--export-all', action='store_true', help='모든 형식으로 내보내기')
    
    args = parser.parse_args()
    
    # 진행률 추적기 초기화
    tracker = RoadmapProgressTracker(args.roadmap_dir)
    
    # 로드맵 파일들 로드
    tracker.load_roadmap_files()
    
    if args.format == 'markdown' or args.export_all:
        # 마크다운 보고서 생성
        report = tracker.generate_progress_report()
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ 마크다운 보고서 저장 완료: {args.output}")
    
    if args.format == 'json' or args.export_all:
        # JSON 내보내기
        tracker.export_to_json()
    
    if args.format == 'yaml' or args.export_all:
        # YAML 내보내기
        tracker.export_to_yaml()
    
    # 콘솔에 요약 출력
    overall_progress = tracker.calculate_overall_progress()
    print(f"\n📊 전체 진행률: {overall_progress['percentage']}%")
    print(f"✅ 완료된 작업: {overall_progress['completed_tasks']}/{overall_progress['total_tasks']}")
    print(f"📅 기간 진행률: {overall_progress['duration_percentage']}%")

if __name__ == "__main__":
    main() 