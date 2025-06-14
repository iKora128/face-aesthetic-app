"""Visual diagnostic report generator using PIL and matplotlib."""

import io
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import seaborn as sns
from loguru import logger

from app.models.analysis import FaceAnalysisResult
from app.utils.exceptions import AnalysisError


class ReportGenerator:
    """Generate beautiful visual diagnostic reports for face analysis."""

    def __init__(self) -> None:
        """Initialize report generator with Korean font support."""
        # Set up matplotlib for Korean text
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False
        
        # Color scheme for beauty reports
        self.colors = {
            'primary': '#ec4899',      # Pink-500 (beauty theme)
            'secondary': '#0ea5e9',    # Sky-500 (Korean theme)
            'success': '#22c55e',      # Green-500
            'warning': '#f59e0b',      # Amber-500  
            'danger': '#ef4444',       # Red-500
            'background': '#fdf2f8',   # Pink-50
            'text_dark': '#1f2937',    # Gray-800
            'text_light': '#6b7280',   # Gray-500
            'border': '#e5e7eb',       # Gray-200
        }
        
        # Beauty level color mapping
        self.level_colors = {
            'SSS級': self.colors['success'],
            'SS級': self.colors['success'],
            'S級': self.colors['primary'],
            'A級': self.colors['primary'],
            'B級': self.colors['secondary'],
            'C級': self.colors['warning'],
            'D級': self.colors['warning'],
            'E級': self.colors['danger'],
            'F級': self.colors['danger'],
            'G級': self.colors['danger'],
        }

    async def generate_report_image(
        self, analysis_result: FaceAnalysisResult, user_name: str = "User"
    ) -> bytes:
        """Generate comprehensive visual report as image bytes."""
        try:
            logger.info("🎨 Generating visual diagnostic report")
            
            # Create figure with subplots
            fig = plt.figure(figsize=(16, 20), facecolor='white')
            
            # Main layout
            gs = fig.add_gridspec(6, 2, height_ratios=[1.5, 1, 1, 1.2, 1, 0.8], 
                                 width_ratios=[1, 1], hspace=0.3, wspace=0.2)
            
            # Header section
            self._create_header(fig, gs[0, :], analysis_result, user_name)
            
            # Overall score section  
            self._create_score_section(fig, gs[1, :], analysis_result)
            
            # Detailed analysis charts
            self._create_radar_chart(fig, gs[2, 0], analysis_result)
            self._create_score_breakdown(fig, gs[2, 1], analysis_result)
            
            # Feature analysis
            self._create_feature_analysis(fig, gs[3, :], analysis_result)
            
            # Recommendations
            self._create_recommendations(fig, gs[4, :], analysis_result)
            
            # Footer
            self._create_footer(fig, gs[5, :])
            
            # Save to bytes
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            plt.close(fig)
            
            img_bytes = img_buffer.getvalue()
            img_buffer.close()
            
            logger.info("✅ Visual report generated successfully")
            return img_bytes
            
        except Exception as e:
            logger.error(f"❌ Report generation failed: {str(e)}")
            raise AnalysisError(
                f"Failed to generate visual report: {str(e)}",
                stage="report_generation"
            ) from e

    def _create_header(
        self, fig: plt.Figure, gs: Any, analysis_result: FaceAnalysisResult, user_name: str
    ) -> None:
        """Create header section with title and overall score."""
        ax = fig.add_subplot(gs)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 5)
        ax.axis('off')
        
        # Background gradient
        gradient = np.linspace(0, 1, 256).reshape(1, -1)
        ax.imshow(gradient, extent=[0, 10, 0, 5], aspect='auto', 
                 cmap='RdPu', alpha=0.1)
        
        # Title
        ax.text(5, 4, 'Face Aesthetic Analysis Report', 
               fontsize=28, fontweight='bold', ha='center', va='center',
               color=self.colors['text_dark'])
        
        # Subtitle with user name
        ax.text(5, 3.3, f'{user_name}様の美容診断結果', 
               fontsize=16, ha='center', va='center',
               color=self.colors['text_light'])
        
        # Overall score display
        score = analysis_result.overall_score.score
        level = analysis_result.overall_score.level
        emoji = analysis_result.overall_score.emoji
        
        # Score circle
        circle = patches.Circle((2, 1.8), 0.8, linewidth=8, 
                              edgecolor=self._get_score_color(score), 
                              facecolor='white')
        ax.add_patch(circle)
        
        # Score number
        ax.text(2, 1.8, f'{score:.1f}', fontsize=32, fontweight='bold',
               ha='center', va='center', color=self._get_score_color(score))
        
        # Level and emoji
        ax.text(8, 2.2, f'{emoji} {level}', fontsize=18, fontweight='bold',
               ha='center', va='center', color=self.colors['text_dark'])
        
        # Description
        description = analysis_result.overall_score.description
        ax.text(8, 1.4, description, fontsize=14, ha='center', va='center',
               color=self.colors['text_light'], wrap=True)

    def _create_score_section(
        self, fig: plt.Figure, gs: Any, analysis_result: FaceAnalysisResult
    ) -> None:
        """Create overall score visualization section."""
        ax = fig.add_subplot(gs)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 3)
        ax.axis('off')
        
        # Score gauge
        score = analysis_result.overall_score.score
        
        # Create semicircle gauge
        theta = np.linspace(0, np.pi, 100)
        x = np.cos(theta)
        y = np.sin(theta)
        
        # Background arc
        ax.plot(x * 2 + 5, y * 2 + 1, linewidth=20, color=self.colors['border'])
        
        # Score arc
        score_theta = np.linspace(0, np.pi * (score / 100), int(100 * score / 100))
        score_x = np.cos(score_theta)
        score_y = np.sin(score_theta)
        ax.plot(score_x * 2 + 5, score_y * 2 + 1, linewidth=20, 
               color=self._get_score_color(score))
        
        # Score markers
        for i, label in enumerate(['0', '25', '50', '75', '100']):
            angle = np.pi * i / 4
            x_pos = np.cos(angle) * 2.3 + 5
            y_pos = np.sin(angle) * 2.3 + 1
            ax.text(x_pos, y_pos, label, fontsize=10, ha='center', va='center',
                   color=self.colors['text_light'])

    def _create_radar_chart(
        self, fig: plt.Figure, gs: Any, analysis_result: FaceAnalysisResult
    ) -> None:
        """Create radar chart for different analysis categories."""
        ax = fig.add_subplot(gs, projection='polar')
        
        # Categories and scores
        categories = ['Eライン', 'パーツ調和', '対称性', '輪郭', '鼻唇角', 'Vライン']
        scores = [
            self._extract_score(analysis_result.eline, 85),
            analysis_result.facial_harmony.harmony_score,
            analysis_result.symmetry.symmetry_score,
            self._extract_score(analysis_result.face_contour, 80),
            self._extract_score(analysis_result.nasolabial_angle, 90),
            analysis_result.vline.vline_score,
        ]
        
        # Convert to 0-100 scale and normalize for radar
        scores = [min(100, max(0, score)) for score in scores]
        
        # Add first point at the end to close the radar
        scores += scores[:1]
        categories += categories[:1]
        
        # Angles for each category
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=True)
        
        # Plot
        ax.plot(angles, scores, 'o-', linewidth=2, color=self.colors['primary'])
        ax.fill(angles, scores, alpha=0.25, color=self.colors['primary'])
        
        # Customize
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories[:-1], fontsize=10)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=8)
        ax.grid(True)
        ax.set_title('各項目スコア', fontsize=14, fontweight='bold', pad=20)

    def _create_score_breakdown(
        self, fig: plt.Figure, gs: Any, analysis_result: FaceAnalysisResult
    ) -> None:
        """Create score breakdown bar chart."""
        ax = fig.add_subplot(gs)
        
        # Get score breakdown
        breakdown = analysis_result.overall_score.detailed_scores
        
        categories = list(breakdown.keys())[:6]  # Top 6 categories
        scores = [breakdown[cat] for cat in categories]
        
        # Create horizontal bar chart
        colors = [self._get_score_color(score) for score in scores]
        bars = ax.barh(categories, scores, color=colors, alpha=0.8)
        
        # Add score labels
        for i, (bar, score) in enumerate(zip(bars, scores)):
            ax.text(score + 1, i, f'{score:.1f}', va='center', fontweight='bold')
        
        ax.set_xlim(0, 100)
        ax.set_xlabel('スコア', fontsize=12)
        ax.set_title('項目別詳細スコア', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)

    def _create_feature_analysis(
        self, fig: plt.Figure, gs: Any, analysis_result: FaceAnalysisResult
    ) -> None:
        """Create feature analysis section."""
        ax = fig.add_subplot(gs)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        ax.axis('off')
        
        # Title
        ax.text(5, 7.5, '詳細分析結果', fontsize=16, fontweight='bold',
               ha='center', va='center', color=self.colors['text_dark'])
        
        # Feature analysis data
        features = [
            ('顔の比率', analysis_result.proportions.evaluation, 
             f'アスペクト比: {analysis_result.proportions.aspect_ratio}'),
            ('Eライン', analysis_result.eline.evaluation,
             f'状態: {analysis_result.eline.status}'),
            ('パーツ調和', analysis_result.facial_harmony.evaluation,
             f'美しさレベル: {analysis_result.facial_harmony.beauty_level}'),
            ('対称性', analysis_result.symmetry.evaluation,
             f'スコア: {analysis_result.symmetry.symmetry_score:.1f}'),
        ]
        
        # Display features in grid
        for i, (name, evaluation, detail) in enumerate(features):
            x = 2.5 if i % 2 == 0 else 7.5
            y = 5.5 - (i // 2) * 2
            
            # Feature box
            rect = patches.Rectangle((x-2, y-0.8), 4, 1.6, linewidth=1,
                                   edgecolor=self.colors['border'],
                                   facecolor=self.colors['background'])
            ax.add_patch(rect)
            
            # Feature name
            ax.text(x, y+0.3, name, fontsize=12, fontweight='bold',
                   ha='center', va='center', color=self.colors['text_dark'])
            
            # Evaluation
            color = self._get_evaluation_color(evaluation)
            ax.text(x, y, evaluation, fontsize=11, fontweight='bold',
                   ha='center', va='center', color=color)
            
            # Detail
            ax.text(x, y-0.3, detail, fontsize=9,
                   ha='center', va='center', color=self.colors['text_light'])

    def _create_recommendations(
        self, fig: plt.Figure, gs: Any, analysis_result: FaceAnalysisResult
    ) -> None:
        """Create recommendations section."""
        ax = fig.add_subplot(gs)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)
        ax.axis('off')
        
        # Title
        ax.text(5, 5.5, '美容アドバイス・改善提案', fontsize=16, fontweight='bold',
               ha='center', va='center', color=self.colors['text_dark'])
        
        # Get recommendations
        advice = analysis_result.beauty_advice[:4]  # Top 4 recommendations
        
        for i, recommendation in enumerate(advice):
            y_pos = 4.5 - i * 0.8
            
            # Bullet point
            ax.text(0.5, y_pos, '•', fontsize=16, fontweight='bold',
                   ha='center', va='center', color=self.colors['primary'])
            
            # Recommendation text
            clean_text = recommendation.replace('⚠️', '').replace('✅', '').replace('💋', '').replace('✨', '').strip()
            ax.text(1, y_pos, clean_text, fontsize=11,
                   ha='left', va='center', color=self.colors['text_dark'],
                   wrap=True)

    def _create_footer(self, fig: plt.Figure, gs: Any) -> None:
        """Create footer with timestamp and disclaimer."""
        ax = fig.add_subplot(gs)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 2)
        ax.axis('off')
        
        # Timestamp
        timestamp = datetime.now().strftime('%Y年%m月%d日 %H:%M')
        ax.text(0.5, 1.5, f'生成日時: {timestamp}', fontsize=10,
               ha='left', va='center', color=self.colors['text_light'])
        
        # Disclaimer
        ax.text(5, 1, '※ この診断結果は美容参考情報であり、医学的アドバイスではありません', 
               fontsize=9, ha='center', va='center', 
               color=self.colors['text_light'], style='italic')
        
        # Logo/Brand
        ax.text(9.5, 1.5, 'Face Aesthetic AI', fontsize=12, fontweight='bold',
               ha='right', va='center', color=self.colors['primary'])

    def _get_score_color(self, score: float) -> str:
        """Get color based on score value."""
        if score >= 90:
            return self.colors['success']
        elif score >= 80:
            return self.colors['primary']
        elif score >= 70:
            return self.colors['secondary']
        elif score >= 60:
            return self.colors['warning']
        else:
            return self.colors['danger']

    def _get_evaluation_color(self, evaluation: str) -> str:
        """Get color based on evaluation text."""
        positive_words = ['理想的', '優秀', '良好', '非常に', '完璧']
        warning_words = ['標準的', 'やや', '普通']
        
        if any(word in evaluation for word in positive_words):
            return self.colors['success']
        elif any(word in evaluation for word in warning_words):
            return self.colors['warning']
        else:
            return self.colors['danger']

    def _extract_score(self, data: Any, default: float = 70.0) -> float:
        """Extract numeric score from analysis data."""
        if hasattr(data, 'score'):
            return float(data.score)
        elif isinstance(data, dict):
            if 'score' in data:
                return float(data['score'])
            elif 'evaluation' in data:
                # Convert evaluation to score
                eval_text = data['evaluation'].lower()
                if '理想' in eval_text or '優秀' in eval_text:
                    return 90.0
                elif '良好' in eval_text:
                    return 80.0
                elif '標準' in eval_text:
                    return 70.0
                else:
                    return 60.0
        return default


# Global instance
_report_generator_instance: ReportGenerator | None = None


def get_report_generator() -> ReportGenerator:
    """Get or create global report generator instance."""
    global _report_generator_instance
    if _report_generator_instance is None:
        _report_generator_instance = ReportGenerator()
    return _report_generator_instance