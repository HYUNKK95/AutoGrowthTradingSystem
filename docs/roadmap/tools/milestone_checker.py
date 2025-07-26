#!/usr/bin/env python3
"""
🎯 마일스톤 체커 (Milestone Checker)

이 스크립트는 AutoGrowthTradingSystem의 마일스톤 달성 여부를 확인하고 알림을 제공합니다.
"""

import os
import re
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import yaml
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class MilestoneChecker:
    def __init__(self, roadmap_dir: str = "docs/roadmap"):
        self.roadmap_dir = Path(roadmap_dir)
        self.milestones = {}
        self.phases = {}
        self.tasks = {}
        self.check_results = {}
        
    def load_milestones(self):
        """마일스톤 정보를 로드합니다."""
        print("🎯 마일스톤 정보 로딩 중...")
        
        # Phase 파일들에서 마일스톤 추출
        phase_files = list(self.roadmap_dir.glob("PHASE_*.md"))
        for phase_file in phase_files:
            self.extract_milestones_from_phase(phase_file)
        
        # 메인 로드맵에서 마일스톤 추출
        main_roadmap = self.roadmap_dir / "MAIN_ROADMAP.md"
        if main_roadmap.exists():
            self.extract_milestones_from_main_roadmap(main_roadmap)
        
        print(f"✅ {len(self.milestones)} 개의 마일스톤 로드 완료")
    
    def extract_milestones_from_phase(self, phase_file: Path):
        """Phase 파일에서 마일스톤을 추출합니다."""
        try:
            with open(phase_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Phase 정보 추출
            phase_info = self.extract_phase_info(content, phase_file.name)
            if phase_info:
                self.phases[phase_info['id']] = phase_info
                
                # 마일스톤 추출
                milestones = self.extract_milestones_from_content(content, phase_info['id'])
                self.milestones.update(milestones)
                
        except Exception as e:
            print(f"❌ {phase_file.name} 마일스톤 추출 실패: {e}")
    
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
        
        return {
            'id': phase_id,
            'title': title,
            'filename': filename,
            'duration': duration
        }
    
    def extract_milestones_from_content(self, content: str, phase_id: str) -> Dict:
        """컨텐츠에서 마일스톤을 추출합니다."""
        milestones = {}
        
        # 마일스톤 패턴 찾기 (예: "### 6.1.1 다중 검증 시스템 (15일)")
        milestone_pattern = r'### (\d+\.\d+(?:\.\d+)?) (.+?) \((\d+)일\)'
        matches = re.finditer(milestone_pattern, content)
        
        for match in matches:
            milestone_id = match.group(1)
            milestone_name = match.group(2).strip()
            duration = int(match.group(3))
            
            # 완료 조건 추출
            completion_conditions = self.extract_completion_conditions(content, milestone_id)
            
            milestone_key = f"{phase_id}.{milestone_id}"
            milestones[milestone_key] = {
                'id': milestone_key,
                'phase_id': phase_id,
                'name': milestone_name,
                'duration': duration,
                'completion_conditions': completion_conditions,
                'status': 'pending',
                'completion_date': None,
                'progress': 0
            }
        
        return milestones
    
    def extract_completion_conditions(self, content: str, milestone_id: str) -> List[str]:
        """완료 조건을 추출합니다."""
        conditions = []
        
        # 마일스톤 섹션 찾기
        section_pattern = rf'### {milestone_id}.*?(?=###|\Z)'
        section_match = re.search(section_pattern, content, re.DOTALL)
        
        if section_match:
            section_content = section_match.group(0)
            
            # 체크리스트 항목들 추출
            checklist_pattern = r'- \[([ x])\] (.+?)(?: \(완료: (\d{4}-\d{2}-\d{2})\))?'
            matches = re.finditer(checklist_pattern, section_content, re.MULTILINE)
            
            for match in matches:
                is_completed = match.group(1) == 'x'
                condition = match.group(2).strip()
                completion_date = match.group(3) if match.group(3) else None
                
                conditions.append({
                    'description': condition,
                    'completed': is_completed,
                    'completion_date': completion_date
                })
        
        return conditions
    
    def extract_milestones_from_main_roadmap(self, main_roadmap: Path):
        """메인 로드맵에서 마일스톤을 추출합니다."""
        try:
            with open(main_roadmap, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 주요 마일스톤 추출
            major_milestones = self.extract_major_milestones(content)
            self.milestones.update(major_milestones)
            
        except Exception as e:
            print(f"❌ 메인 로드맵 마일스톤 추출 실패: {e}")
    
    def extract_major_milestones(self, content: str) -> Dict:
        """주요 마일스톤을 추출합니다."""
        milestones = {}
        
        # 주요 마일스톤 패턴 (예: "Phase 6: 보안 및 규정 준수")
        major_pattern = r'Phase (\d+): (.+?)(?:\n|$)'
        matches = re.finditer(major_pattern, content)
        
        for match in matches:
            phase_id = match.group(1)
            phase_name = match.group(2).strip()
            
            milestone_key = f"major.{phase_id}"
            milestones[milestone_key] = {
                'id': milestone_key,
                'phase_id': phase_id,
                'name': f"Phase {phase_id} 완료: {phase_name}",
                'type': 'major',
                'status': 'pending',
                'completion_date': None,
                'progress': 0
            }
        
        return milestones
    
    def check_milestone_completion(self, milestone_id: str) -> Dict:
        """마일스톤 완료 여부를 확인합니다."""
        milestone = self.milestones.get(milestone_id)
        if not milestone:
            return {'status': 'not_found', 'message': '마일스톤을 찾을 수 없습니다.'}
        
        # 완료 조건 확인
        if 'completion_conditions' in milestone:
            conditions = milestone['completion_conditions']
            completed_conditions = [c for c in conditions if c['completed']]
            
            progress = (len(completed_conditions) / len(conditions)) * 100 if conditions else 0
            is_completed = len(completed_conditions) == len(conditions) and len(conditions) > 0
            
            # 완료일 계산
            completion_date = None
            if is_completed and completed_conditions:
                completion_dates = [c['completion_date'] for c in completed_conditions if c['completion_date']]
                if completion_dates:
                    completion_date = max(completion_dates)
            
            return {
                'status': 'completed' if is_completed else 'in_progress',
                'progress': round(progress, 1),
                'completed_conditions': len(completed_conditions),
                'total_conditions': len(conditions),
                'completion_date': completion_date,
                'message': f"진행률: {progress:.1f}% ({len(completed_conditions)}/{len(conditions)})"
            }
        else:
            # 완료 조건이 없는 경우 (주요 마일스톤)
            return {
                'status': 'pending',
                'progress': 0,
                'message': '완료 조건이 정의되지 않았습니다.'
            }
    
    def check_all_milestones(self):
        """모든 마일스톤을 확인합니다."""
        print("🔍 마일스톤 확인 중...")
        
        for milestone_id in self.milestones.keys():
            result = self.check_milestone_completion(milestone_id)
            self.check_results[milestone_id] = result
            
            # 마일스톤 상태 업데이트
            self.milestones[milestone_id].update(result)
        
        print(f"✅ {len(self.milestones)} 개의 마일스톤 확인 완료")
    
    def generate_milestone_report(self) -> str:
        """마일스톤 보고서를 생성합니다."""
        report = []
        report.append("# 🎯 마일스톤 달성 보고서")
        report.append(f"생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 전체 통계
        total_milestones = len(self.milestones)
        completed_milestones = len([m for m in self.milestones.values() if m['status'] == 'completed'])
        in_progress_milestones = len([m for m in self.milestones.values() if m['status'] == 'in_progress'])
        pending_milestones = len([m for m in self.milestones.values() if m['status'] == 'pending'])
        
        report.append("## 📊 전체 통계")
        report.append(f"- **전체 마일스톤**: {total_milestones}개")
        report.append(f"- **완료**: {completed_milestones}개")
        report.append(f"- **진행 중**: {in_progress_milestones}개")
        report.append(f"- **대기 중**: {pending_milestones}개")
        report.append(f"- **완료율**: {(completed_milestones/total_milestones*100):.1f}%" if total_milestones > 0 else "- **완료율**: 0%")
        report.append("")
        
        # Phase별 마일스톤
        report.append("## 📋 Phase별 마일스톤")
        phases = {}
        for milestone in self.milestones.values():
            phase_id = milestone['phase_id']
            if phase_id not in phases:
                phases[phase_id] = []
            phases[phase_id].append(milestone)
        
        for phase_id in sorted(phases.keys(), key=lambda x: float(x) if x.replace('.', '').isdigit() else x):
            phase_milestones = phases[phase_id]
            completed_count = len([m for m in phase_milestones if m['status'] == 'completed'])
            
            status_emoji = "✅" if completed_count == len(phase_milestones) else "🔄" if completed_count > 0 else "⏳"
            
            report.append(f"### {status_emoji} Phase {phase_id}")
            report.append(f"- **완료**: {completed_count}/{len(phase_milestones)}")
            
            for milestone in phase_milestones:
                milestone_status = "✅" if milestone['status'] == 'completed' else "🔄" if milestone['status'] == 'in_progress' else "⏳"
                report.append(f"  - {milestone_status} {milestone['name']} ({milestone['progress']:.1f}%)")
                if milestone['completion_date']:
                    report.append(f"    - 완료일: {milestone['completion_date']}")
            report.append("")
        
        # 최근 완료된 마일스톤
        recent_completed = [m for m in self.milestones.values() if m['status'] == 'completed' and m['completion_date']]
        recent_completed.sort(key=lambda x: x['completion_date'], reverse=True)
        
        if recent_completed:
            report.append("## ✅ 최근 완료된 마일스톤")
            for milestone in recent_completed[:5]:  # 최근 5개만
                report.append(f"- **{milestone['name']}** (완료: {milestone['completion_date']})")
            report.append("")
        
        # 진행 중인 마일스톤
        in_progress = [m for m in self.milestones.values() if m['status'] == 'in_progress']
        if in_progress:
            report.append("## 🔄 진행 중인 마일스톤")
            for milestone in in_progress:
                report.append(f"- **{milestone['name']}** ({milestone['progress']:.1f}%)")
                if 'completed_conditions' in milestone:
                    report.append(f"  - 조건: {milestone['completed_conditions']}/{milestone['total_conditions']}")
            report.append("")
        
        # 지연된 마일스톤
        delayed_milestones = self.get_delayed_milestones()
        if delayed_milestones:
            report.append("## ⚠️ 지연된 마일스톤")
            for milestone in delayed_milestones:
                report.append(f"- **{milestone['name']}** (예정일: {milestone['expected_date']})")
            report.append("")
        
        return "\n".join(report)
    
    def get_delayed_milestones(self) -> List[Dict]:
        """지연된 마일스톤을 찾습니다."""
        delayed = []
        current_date = datetime.now()
        
        for milestone in self.milestones.values():
            if milestone['status'] != 'completed' and 'duration' in milestone:
                # 간단한 지연 계산 (실제로는 더 복잡한 로직 필요)
                expected_completion = current_date + timedelta(days=milestone['duration'])
                if expected_completion < current_date:
                    milestone['expected_date'] = expected_completion.strftime('%Y-%m-%d')
                    delayed.append(milestone)
        
        return delayed
    
    def send_milestone_notification(self, email_config: Dict):
        """마일스톤 알림을 이메일로 전송합니다."""
        try:
            # 완료된 마일스톤 찾기
            completed_milestones = [m for m in self.milestones.values() if m['status'] == 'completed']
            
            if not completed_milestones:
                print("📧 완료된 마일스톤이 없어 알림을 전송하지 않습니다.")
                return
            
            # 이메일 내용 생성
            subject = f"🎯 마일스톤 달성 알림 - {datetime.now().strftime('%Y-%m-%d')}"
            
            body = []
            body.append("안녕하세요!")
            body.append("")
            body.append("다음 마일스톤이 완료되었습니다:")
            body.append("")
            
            for milestone in completed_milestones:
                body.append(f"✅ {milestone['name']}")
                if milestone['completion_date']:
                    body.append(f"   완료일: {milestone['completion_date']}")
                body.append("")
            
            body.append("축하합니다! 🎉")
            body.append("")
            body.append("자세한 내용은 마일스톤 보고서를 참조하세요.")
            
            email_body = "\n".join(body)
            
            # 이메일 전송
            self.send_email(email_config, subject, email_body)
            print("📧 마일스톤 알림 이메일 전송 완료")
            
        except Exception as e:
            print(f"❌ 이메일 전송 실패: {e}")
    
    def send_email(self, email_config: Dict, subject: str, body: str):
        """이메일을 전송합니다."""
        msg = MIMEMultipart()
        msg['From'] = email_config['from']
        msg['To'] = email_config['to']
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        server.starttls()
        server.login(email_config['username'], email_config['password'])
        server.send_message(msg)
        server.quit()
    
    def export_to_json(self, output_file: str = "milestone_report.json"):
        """마일스톤 데이터를 JSON으로 내보냅니다."""
        data = {
            'generated_at': datetime.now().isoformat(),
            'milestones': self.milestones,
            'check_results': self.check_results,
            'summary': {
                'total': len(self.milestones),
                'completed': len([m for m in self.milestones.values() if m['status'] == 'completed']),
                'in_progress': len([m for m in self.milestones.values() if m['status'] == 'in_progress']),
                'pending': len([m for m in self.milestones.values() if m['status'] == 'pending'])
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON 파일 저장 완료: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='마일스톤 체커')
    parser.add_argument('--roadmap-dir', default='docs/roadmap', help='로드맵 디렉토리 경로')
    parser.add_argument('--output', default='milestone_report.md', help='출력 파일명')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown', help='출력 형식')
    parser.add_argument('--send-email', action='store_true', help='이메일 알림 전송')
    parser.add_argument('--email-config', help='이메일 설정 파일 경로')
    
    args = parser.parse_args()
    
    # 마일스톤 체커 초기화
    checker = MilestoneChecker(args.roadmap_dir)
    
    # 마일스톤 로드
    checker.load_milestones()
    
    # 마일스톤 확인
    checker.check_all_milestones()
    
    if args.format == 'markdown':
        # 마크다운 보고서 생성
        report = checker.generate_milestone_report()
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ 마크다운 보고서 저장 완료: {args.output}")
    
    if args.format == 'json':
        # JSON 내보내기
        checker.export_to_json()
    
    # 이메일 알림 전송
    if args.send_email and args.email_config:
        try:
            with open(args.email_config, 'r', encoding='utf-8') as f:
                email_config = yaml.safe_load(f)
            checker.send_milestone_notification(email_config)
        except Exception as e:
            print(f"❌ 이메일 설정 로드 실패: {e}")
    
    # 콘솔에 요약 출력
    total_milestones = len(checker.milestones)
    completed_milestones = len([m for m in checker.milestones.values() if m['status'] == 'completed'])
    completion_rate = (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0
    
    print(f"\n🎯 마일스톤 완료율: {completion_rate:.1f}%")
    print(f"✅ 완료된 마일스톤: {completed_milestones}/{total_milestones}")

if __name__ == "__main__":
    main() 