#!/usr/bin/env python3
"""
데이터베이스 점검 스크립트
대용량 데이터베이스의 무결성, 성능, 용량을 점검합니다.
"""

import sys
import os
import sqlite3
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import Database

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class DatabaseChecker:
    """데이터베이스 점검 클래스"""
    
    def __init__(self, db_path: str = "data/trading_bot.db"):
        """데이터베이스 점검기 초기화"""
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # 데이터베이스 연결
        self.db = Database()
        
        self.logger.info(f"데이터베이스 점검기 초기화: {db_path}")
    
    def check_database_integrity(self) -> Dict[str, Any]:
        """데이터베이스 무결성 점검"""
        try:
            self.logger.info("=== 데이터베이스 무결성 점검 시작 ===")
            
            integrity_results = {
                'overall_status': 'OK',
                'tables': {},
                'errors': [],
                'warnings': []
            }
            
            # 데이터베이스 연결 테스트
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # 테이블 목록 조회
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    self.logger.info(f"발견된 테이블: {tables}")
                    
                    # 각 테이블 점검
                    for table in tables:
                        table_result = self._check_table_integrity(cursor, table)
                        integrity_results['tables'][table] = table_result
                        
                        if table_result['status'] == 'ERROR':
                            integrity_results['overall_status'] = 'ERROR'
                        elif table_result['status'] == 'WARNING' and integrity_results['overall_status'] == 'OK':
                            integrity_results['overall_status'] = 'WARNING'
                    
                    # 인덱스 점검
                    index_result = self._check_indexes(cursor)
                    integrity_results['indexes'] = index_result
                    
                    # 외래키 제약 조건 점검
                    fk_result = self._check_foreign_keys(cursor)
                    integrity_results['foreign_keys'] = fk_result
                    
            except Exception as e:
                integrity_results['overall_status'] = 'ERROR'
                integrity_results['errors'].append(f"데이터베이스 연결 실패: {e}")
                self.logger.error(f"데이터베이스 연결 실패: {e}")
            
            self.logger.info(f"=== 데이터베이스 무결성 점검 완료: {integrity_results['overall_status']} ===")
            return integrity_results
            
        except Exception as e:
            self.logger.error(f"무결성 점검 실패: {e}")
            return {'overall_status': 'ERROR', 'error': str(e)}
    
    def _check_table_integrity(self, cursor, table_name: str) -> Dict[str, Any]:
        """개별 테이블 무결성 점검"""
        try:
            result = {
                'status': 'OK',
                'row_count': 0,
                'size_bytes': 0,
                'errors': [],
                'warnings': []
            }
            
            # 행 수 조회
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            result['row_count'] = row_count
            
            # 테이블 크기 조회 (간단한 방법으로 변경)
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            result['size_bytes'] = row_count * 100  # 대략적인 크기 추정
            
            # NULL 값 검사
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                is_not_null = col[3]
                
                # NOT NULL 컬럼에서 NULL 값 검사 (안전한 방법)
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NULL")
                    null_count = cursor.fetchone()[0]
                    
                    if null_count > 0:
                        result['status'] = 'WARNING'
                        result['warnings'].append(f"컬럼 '{col_name}'에 {null_count}개의 NULL 값 발견")
                except Exception as e:
                    # 컬럼이 존재하지 않거나 접근할 수 없는 경우 무시
                    pass
            
            # 중복 데이터 검사 (기본키가 있는 경우)
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            pk_columns = [col[1] for col in columns if col[5] > 0]  # pk > 0인 컬럼
            
            if pk_columns:
                pk_cols_str = ', '.join(pk_columns)
                cursor.execute(f"SELECT COUNT(*) FROM (SELECT DISTINCT {pk_cols_str} FROM {table_name})")
                distinct_count = cursor.fetchone()[0]
                
                if distinct_count < row_count:
                    result['status'] = 'ERROR'
                    result['errors'].append(f"기본키 중복 발견: {row_count - distinct_count}개 중복")
            
            self.logger.info(f"테이블 '{table_name}' 점검 완료: {result['status']} ({row_count}행)")
            return result
            
        except Exception as e:
            self.logger.error(f"테이블 '{table_name}' 점검 실패: {e}")
            return {
                'status': 'ERROR',
                'error': str(e),
                'row_count': 0,
                'size_bytes': 0
            }
    
    def _check_indexes(self, cursor) -> Dict[str, Any]:
        """인덱스 점검"""
        try:
            result = {
                'status': 'OK',
                'indexes': [],
                'errors': []
            }
            
            # 인덱스 목록 조회
            cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index'")
            indexes = cursor.fetchall()
            
            for index in indexes:
                index_name, table_name, sql = index
                result['indexes'].append({
                    'name': index_name,
                    'table': table_name,
                    'sql': sql
                })
            
            self.logger.info(f"인덱스 점검 완료: {len(indexes)}개 인덱스")
            return result
            
        except Exception as e:
            self.logger.error(f"인덱스 점검 실패: {e}")
            return {'status': 'ERROR', 'error': str(e)}
    
    def _check_foreign_keys(self, cursor) -> Dict[str, Any]:
        """외래키 제약 조건 점검"""
        try:
            result = {
                'status': 'OK',
                'foreign_keys': [],
                'errors': []
            }
            
            # 외래키 정보 조회
            cursor.execute("PRAGMA foreign_key_list")
            foreign_keys = cursor.fetchall()
            
            for fk in foreign_keys:
                result['foreign_keys'].append({
                    'table': fk[0],
                    'from': fk[3],
                    'to': fk[4],
                    'on_update': fk[5],
                    'on_delete': fk[6]
                })
            
            self.logger.info(f"외래키 점검 완료: {len(foreign_keys)}개 외래키")
            return result
            
        except Exception as e:
            self.logger.error(f"외래키 점검 실패: {e}")
            return {'status': 'ERROR', 'error': str(e)}
    
    def check_database_performance(self) -> Dict[str, Any]:
        """데이터베이스 성능 점검"""
        try:
            self.logger.info("=== 데이터베이스 성능 점검 시작 ===")
            
            performance_results = {
                'query_performance': {},
                'index_efficiency': {},
                'recommendations': []
            }
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 테이블별 행 수 및 크기 조회
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables:
                    # 행 수 조회
                    start_time = time.time()
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    row_count = cursor.fetchone()[0]
                    query_time = time.time() - start_time
                    
                    performance_results['query_performance'][table] = {
                        'row_count': row_count,
                        'count_query_time': query_time,
                        'status': 'FAST' if query_time < 1.0 else 'SLOW'
                    }
                    
                    # 인덱스 효율성 검사
                    if row_count > 10000:  # 큰 테이블만
                        index_efficiency = self._check_index_efficiency(cursor, table)
                        performance_results['index_efficiency'][table] = index_efficiency
                        
                        if index_efficiency['missing_indexes']:
                            performance_results['recommendations'].append(
                                f"테이블 '{table}'에 인덱스 추가 권장"
                            )
                
                # 전체 데이터베이스 크기
                cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                db_size = cursor.fetchone()[0]
                performance_results['database_size'] = db_size
                
                # 페이지 수 및 페이지 크기
                cursor.execute("SELECT page_count, page_size FROM pragma_page_count(), pragma_page_size()")
                page_info = cursor.fetchone()
                performance_results['page_count'] = page_info[0]
                performance_results['page_size'] = page_info[1]
            
            self.logger.info("=== 데이터베이스 성능 점검 완료 ===")
            return performance_results
            
        except Exception as e:
            self.logger.error(f"성능 점검 실패: {e}")
            return {'error': str(e)}
    
    def _check_index_efficiency(self, cursor, table_name: str) -> Dict[str, Any]:
        """인덱스 효율성 검사"""
        try:
            result = {
                'missing_indexes': [],
                'unused_indexes': [],
                'recommendations': []
            }
            
            # 테이블의 컬럼 정보 조회
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # 인덱스 정보 조회
            cursor.execute(f"PRAGMA index_list({table_name})")
            indexes = cursor.fetchall()
            
            # WHERE 절에서 자주 사용되는 컬럼들 (추정)
            frequently_used_columns = ['timestamp', 'symbol', 'interval', 'created_at', 'updated_at']
            
            for col in columns:
                col_name = col[1]
                if col_name in frequently_used_columns:
                    # 해당 컬럼에 인덱스가 있는지 확인
                    has_index = any(index[1].endswith(f"_{col_name}") or col_name in index[1] for index in indexes)
                    
                    if not has_index:
                        result['missing_indexes'].append(col_name)
                        result['recommendations'].append(f"컬럼 '{col_name}'에 인덱스 추가 권장")
            
            return result
            
        except Exception as e:
            self.logger.error(f"인덱스 효율성 검사 실패: {e}")
            return {'error': str(e)}
    
    def check_data_quality(self) -> Dict[str, Any]:
        """데이터 품질 점검"""
        try:
            self.logger.info("=== 데이터 품질 점검 시작 ===")
            
            quality_results = {
                'data_consistency': {},
                'data_completeness': {},
                'data_accuracy': {},
                'issues': []
            }
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 테이블별 데이터 품질 점검
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables:
                    table_quality = self._check_table_data_quality(cursor, table)
                    quality_results['data_consistency'][table] = table_quality
                    
                    if table_quality['issues']:
                        quality_results['issues'].extend(table_quality['issues'])
                
                # 특정 테이블 상세 점검
                if 'price_data' in tables:
                    price_quality = self._check_price_data_quality(cursor)
                    quality_results['data_accuracy']['price_data'] = price_quality
                
                if 'sentiment_data' in tables:
                    sentiment_quality = self._check_sentiment_data_quality(cursor)
                    quality_results['data_accuracy']['sentiment_data'] = sentiment_quality
            
            self.logger.info("=== 데이터 품질 점검 완료 ===")
            return quality_results
            
        except Exception as e:
            self.logger.error(f"데이터 품질 점검 실패: {e}")
            return {'error': str(e)}
    
    def _check_table_data_quality(self, cursor, table_name: str) -> Dict[str, Any]:
        """테이블별 데이터 품질 점검"""
        try:
            result = {
                'total_rows': 0,
                'null_counts': {},
                'duplicate_rows': 0,
                'issues': []
            }
            
            # 전체 행 수
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            result['total_rows'] = cursor.fetchone()[0]
            
            # 컬럼별 NULL 값 수
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                col_name = col[1]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NULL")
                null_count = cursor.fetchone()[0]
                result['null_counts'][col_name] = null_count
                
                if null_count > 0:
                    result['issues'].append(f"컬럼 '{col_name}'에 {null_count}개의 NULL 값")
            
            # 중복 행 검사 (모든 컬럼 기준)
            if columns:
                col_names = [col[1] for col in columns]
                cols_str = ', '.join(col_names)
                cursor.execute(f"SELECT COUNT(*) FROM (SELECT DISTINCT {cols_str} FROM {table_name})")
                distinct_count = cursor.fetchone()[0]
                result['duplicate_rows'] = result['total_rows'] - distinct_count
                
                if result['duplicate_rows'] > 0:
                    result['issues'].append(f"{result['duplicate_rows']}개의 중복 행 발견")
            
            return result
            
        except Exception as e:
            self.logger.error(f"테이블 '{table_name}' 데이터 품질 점검 실패: {e}")
            return {'error': str(e)}
    
    def _check_price_data_quality(self, cursor) -> Dict[str, Any]:
        """가격 데이터 품질 점검"""
        try:
            result = {
                'total_records': 0,
                'symbols': [],
                'intervals': [],
                'date_range': {},
                'anomalies': []
            }
            
            # 전체 레코드 수
            cursor.execute("SELECT COUNT(*) FROM price_data")
            result['total_records'] = cursor.fetchone()[0]
            
            # 심볼별 통계
            cursor.execute("SELECT symbol, COUNT(*) FROM price_data GROUP BY symbol")
            symbol_stats = cursor.fetchall()
            result['symbols'] = [stat[0] for stat in symbol_stats]
            
            # 간격별 통계
            cursor.execute("SELECT interval, COUNT(*) FROM price_data GROUP BY interval")
            interval_stats = cursor.fetchall()
            result['intervals'] = [stat[0] for stat in interval_stats]
            
            # 날짜 범위
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM price_data")
            date_range = cursor.fetchone()
            if date_range[0] and date_range[1]:
                result['date_range'] = {
                    'start': datetime.fromtimestamp(date_range[0] / 1000),
                    'end': datetime.fromtimestamp(date_range[1] / 1000)
                }
            
            # 이상치 검사 (가격이 0이거나 음수인 경우)
            cursor.execute("SELECT COUNT(*) FROM price_data WHERE open <= 0 OR high <= 0 OR low <= 0 OR close <= 0")
            anomaly_count = cursor.fetchone()[0]
            if anomaly_count > 0:
                result['anomalies'].append(f"{anomaly_count}개의 이상한 가격 데이터")
            
            return result
            
        except Exception as e:
            self.logger.error(f"가격 데이터 품질 점검 실패: {e}")
            return {'error': str(e)}
    
    def _check_sentiment_data_quality(self, cursor) -> Dict[str, Any]:
        """감정 데이터 품질 점검"""
        try:
            result = {
                'total_records': 0,
                'sources': [],
                'sentiment_range': {},
                'issues': []
            }
            
            # 전체 레코드 수
            cursor.execute("SELECT COUNT(*) FROM sentiment_data")
            result['total_records'] = cursor.fetchone()[0]
            
            # 소스별 통계
            cursor.execute("SELECT source, COUNT(*) FROM sentiment_data GROUP BY source")
            source_stats = cursor.fetchall()
            result['sources'] = [stat[0] for stat in source_stats]
            
            # 감정 점수 범위
            cursor.execute("SELECT MIN(sentiment_score), MAX(sentiment_score), AVG(sentiment_score) FROM sentiment_data")
            score_stats = cursor.fetchone()
            if score_stats[0] is not None:
                result['sentiment_range'] = {
                    'min': score_stats[0],
                    'max': score_stats[1],
                    'avg': score_stats[2]
                }
            
            # 감정 점수 이상치 검사
            cursor.execute("SELECT COUNT(*) FROM sentiment_data WHERE sentiment_score < -1 OR sentiment_score > 1")
            anomaly_count = cursor.fetchone()[0]
            if anomaly_count > 0:
                result['issues'].append(f"{anomaly_count}개의 이상한 감정 점수")
            
            return result
            
        except Exception as e:
            self.logger.error(f"감정 데이터 품질 점검 실패: {e}")
            return {'error': str(e)}
    
    def generate_report(self) -> str:
        """종합 점검 리포트 생성"""
        try:
            self.logger.info("=== 데이터베이스 종합 점검 리포트 생성 시작 ===")
            
            # 각종 점검 실행
            integrity_result = self.check_database_integrity()
            performance_result = self.check_database_performance()
            quality_result = self.check_data_quality()
            
            # 리포트 생성
            report = self._generate_html_report(integrity_result, performance_result, quality_result)
            
            # 리포트 파일 저장
            report_file = f"database_check_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            self.logger.info(f"=== 데이터베이스 점검 리포트 생성 완료: {report_file} ===")
            return report_file
            
        except Exception as e:
            self.logger.error(f"리포트 생성 실패: {e}")
            return None
    
    def _generate_html_report(self, integrity_result: Dict, performance_result: Dict, quality_result: Dict) -> str:
        """HTML 리포트 생성"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>데이터베이스 점검 리포트</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .status-ok {{ color: green; }}
        .status-warning {{ color: orange; }}
        .status-error {{ color: red; }}
        .table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        .table th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .table th {{ background-color: #f2f2f2; }}
        .recommendation {{ background-color: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 데이터베이스 점검 리포트</h1>
        <p>생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>데이터베이스: {self.db_path}</p>
    </div>
    
    <div class="section">
        <h2>🔍 무결성 점검 결과</h2>
        <p>전체 상태: <span class="status-{integrity_result.get('overall_status', 'unknown')}">{integrity_result.get('overall_status', 'UNKNOWN')}</span></p>
        
        <h3>테이블별 상태</h3>
        <table class="table">
            <tr>
                <th>테이블명</th>
                <th>상태</th>
                <th>행 수</th>
                <th>크기 (바이트)</th>
                <th>문제점</th>
            </tr>
"""
        
        for table_name, table_result in integrity_result.get('tables', {}).items():
            status_class = f"status-{table_result.get('status', 'unknown').lower()}"
            issues = ', '.join(table_result.get('errors', []) + table_result.get('warnings', []))
            
            html += f"""
            <tr>
                <td>{table_name}</td>
                <td class="{status_class}">{table_result.get('status', 'UNKNOWN')}</td>
                <td>{table_result.get('row_count', 0):,}</td>
                <td>{table_result.get('size_bytes', 0):,}</td>
                <td>{issues if issues else '없음'}</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
    
    <div class="section">
        <h2>⚡ 성능 점검 결과</h2>
"""
        
        if 'database_size' in performance_result:
            db_size_mb = performance_result['database_size'] / (1024 * 1024)
            html += f"""
        <p>데이터베이스 크기: {db_size_mb:.2f} MB</p>
        <p>페이지 수: {performance_result.get('page_count', 0):,}</p>
        <p>페이지 크기: {performance_result.get('page_size', 0):,} 바이트</p>
"""
        
        html += """
        <h3>쿼리 성능</h3>
        <table class="table">
            <tr>
                <th>테이블명</th>
                <th>행 수</th>
                <th>카운트 쿼리 시간</th>
                <th>상태</th>
            </tr>
"""
        
        for table_name, perf_result in performance_result.get('query_performance', {}).items():
            status_class = f"status-{perf_result.get('status', 'unknown').lower()}"
            html += f"""
            <tr>
                <td>{table_name}</td>
                <td>{perf_result.get('row_count', 0):,}</td>
                <td>{perf_result.get('count_query_time', 0):.3f}초</td>
                <td class="{status_class}">{perf_result.get('status', 'UNKNOWN')}</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
    
    <div class="section">
        <h2>📈 데이터 품질 점검 결과</h2>
"""
        
        for table_name, quality_result_table in quality_result.get('data_consistency', {}).items():
            html += f"""
        <h3>{table_name}</h3>
        <p>전체 행 수: {quality_result_table.get('total_rows', 0):,}</p>
        <p>중복 행 수: {quality_result_table.get('duplicate_rows', 0):,}</p>
"""
            
            if quality_result_table.get('issues'):
                html += '<ul>'
                for issue in quality_result_table['issues']:
                    html += f'<li>{issue}</li>'
                html += '</ul>'
        
        html += """
    </div>
    
    <div class="section">
        <h2>💡 권장사항</h2>
"""
        
        recommendations = []
        
        # 성능 권장사항
        for table_name, perf_result in performance_result.get('query_performance', {}).items():
            if perf_result.get('status') == 'SLOW':
                recommendations.append(f"테이블 '{table_name}'에 인덱스 추가 고려")
        
        # 무결성 권장사항
        for table_name, integrity_table in integrity_result.get('tables', {}).items():
            if integrity_table.get('status') == 'ERROR':
                recommendations.append(f"테이블 '{table_name}'의 무결성 문제 해결 필요")
        
        if recommendations:
            for rec in recommendations:
                html += f'<div class="recommendation">💡 {rec}</div>'
        else:
            html += '<p>현재 특별한 권장사항이 없습니다.</p>'
        
        html += """
    </div>
</body>
</html>
"""
        
        return html
    
    def print_summary(self):
        """점검 결과 요약 출력"""
        try:
            self.logger.info("=== 데이터베이스 점검 요약 ===")
            
            # 무결성 점검
            integrity_result = self.check_database_integrity()
            print(f"🔍 무결성 상태: {integrity_result.get('overall_status', 'UNKNOWN')}")
            
            # 성능 점검
            performance_result = self.check_database_performance()
            if 'database_size' in performance_result:
                db_size_mb = performance_result['database_size'] / (1024 * 1024)
                print(f"📊 데이터베이스 크기: {db_size_mb:.2f} MB")
            
            # 데이터 품질 점검
            quality_result = self.check_data_quality()
            total_issues = len(quality_result.get('issues', []))
            print(f"📈 발견된 문제점: {total_issues}개")
            
            print("="*50)
            
        except Exception as e:
            self.logger.error(f"요약 출력 실패: {e}")

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='데이터베이스 점검 스크립트')
    parser.add_argument('--db-path', type=str, default='data/trading_bot.db', help='데이터베이스 파일 경로')
    parser.add_argument('--integrity', action='store_true', help='무결성 점검만 실행')
    parser.add_argument('--performance', action='store_true', help='성능 점검만 실행')
    parser.add_argument('--quality', action='store_true', help='데이터 품질 점검만 실행')
    parser.add_argument('--report', action='store_true', help='HTML 리포트 생성')
    parser.add_argument('--summary', action='store_true', help='요약 정보만 출력')
    
    args = parser.parse_args()
    
    try:
        checker = DatabaseChecker(args.db_path)
        
        if args.summary:
            checker.print_summary()
        elif args.integrity:
            result = checker.check_database_integrity()
            print(f"무결성 점검 결과: {result['overall_status']}")
        elif args.performance:
            result = checker.check_database_performance()
            print("성능 점검 완료")
        elif args.quality:
            result = checker.check_data_quality()
            print("데이터 품질 점검 완료")
        elif args.report:
            report_file = checker.generate_report()
            if report_file:
                print(f"리포트 생성 완료: {report_file}")
        else:
            # 전체 점검
            checker.print_summary()
            report_file = checker.generate_report()
            if report_file:
                print(f"리포트 생성 완료: {report_file}")
        
    except Exception as e:
        logger.error(f"데이터베이스 점검 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 