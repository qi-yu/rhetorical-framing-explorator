import { parse } from 'papaparse';
import { Component } from '@angular/core';
import { FeatureService } from '../feature-selection/feature.service';
import { forkJoin } from 'rxjs';
import { IFeature } from '../feature-selection/feature';

@Component({
  selector: 'app-statistics',
  templateUrl: './statistics.component.html',
  styleUrls: ['./statistics.component.css']
})
export class StatisticsComponent {
  selectedFeatures: Array<IFeature> = [];
  featureStatistics: Array<any> = [];
  featureSums: Array<number> = [];
  labels: Array<string> = [];
  data: any;
  options: any;

  constructor(private featureService: FeatureService) {}

  downloadStatistics(): void {
    this.featureService.getFeatureStatistics()
      .subscribe({
        next: data => {
          const blob = new Blob([data], { type: 'text/csv' });
          const link = document.createElement('a');
          
          link.href = window.URL.createObjectURL(blob);
          link.download = 'feature_statistics.csv';
          link.click();
        }, 

        error: (error) => {
          console.error('Error downloading feature statistics:', error);
        }
      });
  }


  setDataForPlot(labels: Array<string>, featureSums: Array<number>): void {
    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--text-color');
    const textColorSecondary = documentStyle.getPropertyValue('--text-color-secondary');
    const surfaceBorder = documentStyle.getPropertyValue('--surface-border');

    this.data = {
      labels: labels,
      datasets: [{
        label: 'Dataset 1',
        data: featureSums
      }]
    }

    this.options = {
      maintainAspectRatio: false,
      aspectRatio: 0.8,
      plugins: {
          legend: {
              labels: {
                  color: textColor
              }
          }
      },
      scales: {
          x: {
              ticks: {
                  color: textColorSecondary,
                  font: {
                      weight: 500
                  }
              },
              grid: {
                  color: surfaceBorder,
                  drawBorder: false
              }
          },
          y: {
              ticks: {
                  color: textColorSecondary
              },
              grid: {
                  color: surfaceBorder,
                  drawBorder: false
              }
          }

      }
    };
  }


  makePlot(): void {
    this.featureService.selectedFeatures$
      .subscribe((features) => {
        this.selectedFeatures = features;
      });

    this.featureService.getFeatureStatistics()
      .subscribe({
        next: (raw) => {
          this.featureStatistics = parse(raw, { delimiter: "\t", header: true }).data.slice(0, -1)

          const sums: { [key: string]: number } = {};
    
          this.featureStatistics.forEach((obj) => {
            this.selectedFeatures.forEach((feature) => {
              sums[feature.annotation_method] = (sums[feature.annotation_method] || 0) + parseInt(obj[feature.annotation_method], 10);
            });
          });

          this.featureSums = this.selectedFeatures.map(feature => sums[feature.annotation_method]);
          this.setDataForPlot(this.selectedFeatures.map(feature => feature.name), this.featureSums)
        }
      }) 
  }

  ngOnInit() {
    this.makePlot();    
  }  
}
