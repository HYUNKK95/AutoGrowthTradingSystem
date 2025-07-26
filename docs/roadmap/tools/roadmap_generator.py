#!/usr/bin/env python3
"""
🚀 로드맵 생성기 (Roadmap Generator)

이 스크립트는 AutoGrowthTradingSystem의 새로운 Phase나 작업을 자동으로 생성합니다.
"""

import os
import re
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import yaml
import jinja2

class RoadmapGenerator:
    def __init__(self, roadmap_dir: str = "docs/roadmap"):
        self.roadmap_dir = Path(roadmap_dir)
        self.templates_dir = self.roadmap_dir / "templates"
        self.existing_phases = {}
        self.template_engine = None
        
        # 템플릿 엔진 초기화
        self.init_template_engine()
        
    def init_template_engine(self):
        """Jinja2 템플릿 엔진을 초기화합니다."""
        if self.templates_dir.exists():
            self.template_engine = jinja2.Environment(
                loader=jinja2.FileSystemLoader(str(self.templates_dir)),
                autoescape=True,
                trim_blocks=True,
                lstrip_blocks=True
            )
        else:
            print(f"⚠️ 템플릿 디렉토리가 없습니다: {self.templates_dir}")
    
    def load_existing_phases(self):
        """기존 Phase들을 로드합니다."""
        print("📁 기존 Phase 로딩 중...")
        
        phase_files = list(self.roadmap_dir.glob("PHASE_*.md"))
        for phase_file in phase_files:
            phase_info = self.extract_phase_info(phase_file)
            if phase_info:
                self.existing_phases[phase_info['id']] = phase_info
        
        print(f"✅ {len(self.existing_phases)} 개의 기존 Phase 로드 완료")
    
    def extract_phase_info(self, phase_file: Path) -> Optional[Dict]:
        """Phase 파일에서 정보를 추출합니다."""
        try:
            with open(phase_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
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
            
            # 예산 추출 (개인 개발자 기준으로 수정)
            budget_match = re.search(r'예산.*?\$([\d,]+)', content)
            budget = int(budget_match.group(1).replace(',', '')) if budget_match else 0
            
            return {
                'id': phase_id,
                'title': title,
                'filename': phase_file.name,
                'duration': duration,
                'budget': budget
            }
            
        except Exception as e:
            print(f"❌ {phase_file.name} 정보 추출 실패: {e}")
            return None
    
    def get_next_phase_id(self) -> str:
        """다음 Phase ID를 생성합니다."""
        if not self.existing_phases:
            return "1"
        
        # 기존 Phase ID들 추출
        phase_ids = []
        for phase_id in self.existing_phases.keys():
            try:
                phase_ids.append(float(phase_id))
            except ValueError:
                # 숫자가 아닌 ID는 무시
                continue
        
        if not phase_ids:
            return "1"
        
        # 다음 ID 계산
        next_id = max(phase_ids) + 1
        return str(int(next_id)) if next_id.is_integer() else str(next_id)
    
    def generate_phase_template(self, phase_id: str, title: str, duration: int, budget: int = 0) -> str:
        """Phase 템플릿을 생성합니다."""
        if self.template_engine and self.template_engine.get_template("phase_template.md"):
            # 템플릿 파일이 있는 경우
            template = self.template_engine.get_template("phase_template.md")
            return template.render(
                phase_id=phase_id,
                title=title,
                duration=duration,
                budget=budget,
                generated_date=datetime.now().strftime('%Y-%m-%d'),
                dependencies=self.get_phase_dependencies(phase_id)
            )
        else:
            # 기본 템플릿 생성
            return self.generate_default_phase_template(phase_id, title, duration, budget)
    
    def generate_default_phase_template(self, phase_id: str, title: str, duration: int, budget: int) -> str:
        """기본 Phase 템플릿을 생성합니다."""
        template = f"""# 🚀 Phase {phase_id}: {title}

## 📊 전체 개요
- **기간**: {duration}일
- **개발자**: 1명 (AI 도구 활용)
- **예산**: ${budget:,} (개인 개발 기준)
- **목표**: {title} 구현 및 검증

## 📋 주요 작업

### {phase_id}.1 핵심 기능 개발 ({duration//2}일)
**의존성**: 이전 Phase 완료
**개발자**: 1명 (AI 도구 활용)

**세부 작업**:
- [ ] {phase_id}.1.1 기본 기능 구현 ({duration//4}일)
  - 핵심 기능 설계
  - 기본 구현
  - 단위 테스트
- [ ] {phase_id}.1.2 고급 기능 구현 ({duration//4}일)
  - 고급 기능 설계
  - 구현 및 테스트
  - 성능 최적화

### {phase_id}.2 테스트 및 검증 ({duration//2}일)
**의존성**: {phase_id}.1 완료
**개발자**: 1명 (자체 테스트)

**세부 작업**:
- [ ] {phase_id}.2.1 통합 테스트 ({duration//4}일)
  - 통합 테스트 계획
  - 테스트 실행
  - 버그 수정
- [ ] {phase_id}.2.2 사용자 테스트 ({duration//4}일)
  - 사용자 테스트 계획
  - 피드백 수집
  - 개선 사항 적용

## 🎯 성과 지표
- **기능 완성도**: 100%
- **테스트 커버리지**: 80% 이상 (개인 개발 기준)
- **성능 목표**: < 200ms 응답시간 (개인 서버 기준)
- **개발 효율성**: AI 도구 활용 최적화

## 📊 다음 단계
1. **Phase {int(float(phase_id)) + 1} 준비**
2. **개발 효율성 분석**
3. **성능 최적화 계획**

---

**생성일**: {datetime.now().strftime('%Y-%m-%d')}
**버전**: 1.0.0
**개발자**: 개인 개발자 (AI 도구 활용)
"""
        return template
    
    def get_phase_dependencies(self, phase_id: str) -> List[str]:
        """Phase 의존성을 계산합니다."""
        try:
            current_phase_num = float(phase_id)
            dependencies = []
            
            # 이전 Phase들을 의존성으로 추가
            for existing_id in self.existing_phases.keys():
                try:
                    existing_num = float(existing_id)
                    if existing_num < current_phase_num:
                        dependencies.append(f"Phase {existing_id}")
                except ValueError:
                    continue
            
            return dependencies
        except ValueError:
            return []
    
    def generate_task_template(self, task_name: str, duration: int, phase_id: str = None) -> str:
        """작업 템플릿을 생성합니다."""
        if self.template_engine and self.template_engine.get_template("task_template.md"):
            template = self.template_engine.get_template("task_template.md")
            return template.render(
                task_name=task_name,
                duration=duration,
                phase_id=phase_id,
                generated_date=datetime.now().strftime('%Y-%m-%d')
            )
        else:
            return self.generate_default_task_template(task_name, duration, phase_id)
    
    def generate_default_task_template(self, task_name: str, duration: int, phase_id: str = None) -> str:
        """기본 작업 템플릿을 생성합니다."""
        template = f"""# 📋 작업: {task_name}

## 📊 작업 개요
- **작업명**: {task_name}
- **기간**: {duration}일
- **Phase**: {phase_id if phase_id else '미정'}
- **우선순위**: 높음
- **상태**: 계획됨

## 🎯 목표
- {task_name} 완료
- 품질 기준 충족
- 문서화 완료

## 📋 세부 작업
- [ ] 요구사항 분석 (1일)
- [ ] 설계 및 계획 (1일)
- [ ] 구현 ({duration-4}일)
- [ ] 테스트 (1일)
- [ ] 문서화 (1일)

## ✅ 완료 기준
- [ ] 기능 구현 완료
- [ ] 단위 테스트 통과
- [ ] 코드 리뷰 완료
- [ ] 문서 작성 완료

## 📊 성과 지표
- **완료율**: 100%
- **품질 점수**: 90% 이상
- **테스트 커버리지**: 80% 이상

## 🔗 관련 링크
- [요구사항 문서]()
- [설계 문서]()
- [테스트 계획]()

---

**생성일**: {datetime.now().strftime('%Y-%m-%d')}
**담당자**: 개발팀
"""
        return template
    
    def generate_milestone_template(self, milestone_name: str, target_date: str, phase_id: str = None) -> str:
        """마일스톤 템플릿을 생성합니다."""
        if self.template_engine and self.template_engine.get_template("milestone_template.md"):
            template = self.template_engine.get_template("milestone_template.md")
            return template.render(
                milestone_name=milestone_name,
                target_date=target_date,
                phase_id=phase_id,
                generated_date=datetime.now().strftime('%Y-%m-%d')
            )
        else:
            return self.generate_default_milestone_template(milestone_name, target_date, phase_id)
    
    def generate_default_milestone_template(self, milestone_name: str, target_date: str, phase_id: str = None) -> str:
        """기본 마일스톤 템플릿을 생성합니다."""
        template = f"""# 🎯 마일스톤: {milestone_name}

## 📊 마일스톤 개요
- **마일스톤명**: {milestone_name}
- **목표일**: {target_date}
- **Phase**: {phase_id if phase_id else '전체'}
- **상태**: 계획됨

## 🎯 목표
- {milestone_name} 달성
- 품질 기준 충족
- 사용자 만족도 달성

## 📋 전제 조건
- [ ] 모든 필수 작업 완료
- [ ] 품질 검증 통과
- [ ] 사용자 승인

## ✅ 성공 기준
- [ ] 기능 완성도 100%
- [ ] 성능 목표 달성
- [ ] 보안 요구사항 충족
- [ ] 사용자 테스트 통과

## 📊 진행 상황
- **전체 진행률**: 0%
- **완료된 작업**: 0개
- **남은 작업**: 미정

## 🔗 관련 문서
- [프로젝트 계획]()
- [요구사항 문서]()
- [테스트 계획]()

---

**생성일**: {datetime.now().strftime('%Y-%m-%d')}
**담당자**: 프로젝트 매니저
"""
        return template
    
    def create_phase_file(self, phase_id: str, title: str, duration: int, budget: int = 0) -> str:
        """Phase 파일을 생성합니다."""
        content = self.generate_phase_template(phase_id, title, duration, budget)
        filename = f"PHASE_{phase_id.replace('.', '_')}_{title.replace(' ', '_').replace('/', '_')}.md"
        filepath = self.roadmap_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Phase 파일 생성 완료: {filepath}")
        return str(filepath)
    
    def create_task_file(self, task_name: str, duration: int, phase_id: str = None) -> str:
        """작업 파일을 생성합니다."""
        content = self.generate_task_template(task_name, duration, phase_id)
        filename = f"TASK_{task_name.replace(' ', '_').replace('/', '_')}.md"
        filepath = self.roadmap_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 작업 파일 생성 완료: {filepath}")
        return str(filepath)
    
    def create_milestone_file(self, milestone_name: str, target_date: str, phase_id: str = None) -> str:
        """마일스톤 파일을 생성합니다."""
        content = self.generate_milestone_template(milestone_name, target_date, phase_id)
        filename = f"MILESTONE_{milestone_name.replace(' ', '_').replace('/', '_')}.md"
        filepath = self.roadmap_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 마일스톤 파일 생성 완료: {filepath}")
        return str(filepath)
    
    def create_template_files(self):
        """기본 템플릿 파일들을 생성합니다."""
        if not self.templates_dir.exists():
            self.templates_dir.mkdir(parents=True)
        
        # Phase 템플릿
        phase_template = """# 🚀 Phase {{ phase_id }}: {{ title }}

## 📊 전체 개요
- **기간**: {{ duration }}일
- **인력**: 개발자 2명, 디자이너 1명
- **예산**: ${{ "{:,}".format(budget) }}
- **목표**: {{ title }} 구현 및 검증

## 📋 주요 작업

{% for i in range(1, 4) %}
### {{ phase_id }}.{{ i }} 주요 작업 ({{ duration//3 }}일)
**의존성**: {% if i > 1 %}{{ phase_id }}.{{ i-1 }} 완료{% else %}이전 Phase 완료{% endif %}
**리소스**: 개발자 2명

**세부 작업**:
- [ ] {{ phase_id }}.{{ i }}.1 기본 구현 ({{ duration//6 }}일)
- [ ] {{ phase_id }}.{{ i }}.2 고급 기능 ({{ duration//6 }}일)
- [ ] {{ phase_id }}.{{ i }}.3 테스트 및 검증 ({{ duration//6 }}일)
{% endfor %}

## 🎯 성과 지표
- **기능 완성도**: 100%
- **테스트 커버리지**: 90% 이상
- **성능 목표**: < 100ms 응답시간

## 📊 다음 단계
1. **Phase {{ (phase_id|float + 1)|int }} 준비**
2. **사용자 피드백 분석**

---

**생성일**: {{ generated_date }}
**버전**: 1.0.0
**담당자**: 개발팀
"""
        
        # 작업 템플릿
        task_template = """# 📋 작업: {{ task_name }}

## 📊 작업 개요
- **작업명**: {{ task_name }}
- **기간**: {{ duration }}일
- **Phase**: {{ phase_id if phase_id else '미정' }}
- **우선순위**: 높음

## 🎯 목표
- {{ task_name }} 완료
- 품질 기준 충족

## 📋 세부 작업
- [ ] 요구사항 분석 (1일)
- [ ] 설계 및 계획 (1일)
- [ ] 구현 ({{ duration-4 }}일)
- [ ] 테스트 (1일)
- [ ] 문서화 (1일)

## ✅ 완료 기준
- [ ] 기능 구현 완료
- [ ] 테스트 통과
- [ ] 문서 작성 완료

---

**생성일**: {{ generated_date }}
**담당자**: 개발팀
"""
        
        # 마일스톤 템플릿
        milestone_template = """# 🎯 마일스톤: {{ milestone_name }}

## 📊 마일스톤 개요
- **마일스톤명**: {{ milestone_name }}
- **목표일**: {{ target_date }}
- **Phase**: {{ phase_id if phase_id else '전체' }}

## 🎯 목표
- {{ milestone_name }} 달성
- 품질 기준 충족

## ✅ 성공 기준
- [ ] 기능 완성도 100%
- [ ] 성능 목표 달성
- [ ] 사용자 테스트 통과

## 📊 진행 상황
- **전체 진행률**: 0%
- **완료된 작업**: 0개

---

**생성일**: {{ generated_date }}
**담당자**: 프로젝트 매니저
"""
        
        # 템플릿 파일들 생성
        templates = {
            'phase_template.md': phase_template,
            'task_template.md': task_template,
            'milestone_template.md': milestone_template
        }
        
        for filename, content in templates.items():
            filepath = self.templates_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 템플릿 파일 생성 완료: {filepath}")
    
    def generate_roadmap_summary(self) -> str:
        """로드맵 요약을 생성합니다."""
        summary = []
        summary.append("# 🗺️ 로드맵 요약")
        summary.append(f"생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")
        
        summary.append("## 📋 Phase 목록")
        for phase_id in sorted(self.existing_phases.keys(), key=lambda x: float(x)):
            phase = self.existing_phases[phase_id]
            summary.append(f"### Phase {phase_id}: {phase['title']}")
            summary.append(f"- **기간**: {phase['duration']['min']}-{phase['duration']['max']}일")
            summary.append(f"- **예산**: ${phase['budget']:,}")
            summary.append(f"- **파일**: {phase['filename']}")
            summary.append("")
        
        return "\n".join(summary)

def main():
    parser = argparse.ArgumentParser(description='로드맵 생성기')
    parser.add_argument('--roadmap-dir', default='docs/roadmap', help='로드맵 디렉토리 경로')
    parser.add_argument('--type', choices=['phase', 'task', 'milestone', 'template'], required=True, help='생성할 타입')
    parser.add_argument('--name', help='Phase/작업/마일스톤 이름')
    parser.add_argument('--duration', type=int, help='기간 (일)')
    parser.add_argument('--budget', type=int, default=0, help='예산')
    parser.add_argument('--phase-id', help='Phase ID (자동 생성 시 생략)')
    parser.add_argument('--target-date', help='목표일 (마일스톤용)')
    parser.add_argument('--create-templates', action='store_true', help='기본 템플릿 파일들 생성')
    
    args = parser.parse_args()
    
    # 로드맵 생성기 초기화
    generator = RoadmapGenerator(args.roadmap_dir)
    
    # 기존 Phase 로드
    generator.load_existing_phases()
    
    if args.create_templates:
        # 템플릿 파일들 생성
        generator.create_template_files()
        return
    
    if args.type == 'phase':
        if not args.name:
            print("❌ Phase 이름을 지정해주세요 (--name)")
            return
        
        if not args.duration:
            print("❌ 기간을 지정해주세요 (--duration)")
            return
        
        # Phase ID 자동 생성 또는 사용자 지정
        phase_id = args.phase_id if args.phase_id else generator.get_next_phase_id()
        
        # Phase 파일 생성
        generator.create_phase_file(phase_id, args.name, args.duration, args.budget)
        
    elif args.type == 'task':
        if not args.name:
            print("❌ 작업 이름을 지정해주세요 (--name)")
            return
        
        if not args.duration:
            print("❌ 기간을 지정해주세요 (--duration)")
            return
        
        # 작업 파일 생성
        generator.create_task_file(args.name, args.duration, args.phase_id)
        
    elif args.type == 'milestone':
        if not args.name:
            print("❌ 마일스톤 이름을 지정해주세요 (--name)")
            return
        
        if not args.target_date:
            print("❌ 목표일을 지정해주세요 (--target-date)")
            return
        
        # 마일스톤 파일 생성
        generator.create_milestone_file(args.name, args.target_date, args.phase_id)
    
    # 로드맵 요약 생성
    summary = generator.generate_roadmap_summary()
    summary_file = generator.roadmap_dir / "ROADMAP_SUMMARY.md"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"✅ 로드맵 요약 생성 완료: {summary_file}")

if __name__ == "__main__":
    main() 