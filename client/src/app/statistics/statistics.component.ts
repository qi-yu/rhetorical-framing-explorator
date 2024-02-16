import { parse } from 'papaparse';
import { Component } from '@angular/core';
import { FeatureService } from '../feature-selection/feature.service';
import { IFeature } from '../feature-selection/feature';

@Component({
  selector: 'app-statistics',
  templateUrl: './statistics.component.html',
  styleUrls: ['./statistics.component.css']
})
export class StatisticsComponent {
  selectedFeatures: Array<IFeature> = [];
  selectedNonAuxiliaryFeatures: Array<IFeature> = [];
  byGroupPlotData: any;
  byGroupPlotOptions: any;
  tokenCountPlotData: any;
  tokenCountPlotOptions: any;

  constructor(private featureService: FeatureService) {}

  downloadStatistics(): void {
    this.featureService.getFeatureStatistics()
      .subscribe({
        next: data => {
          const blob = new Blob([data], { type: 'application/zip' });
          const link = document.createElement('a');
          
          link.href = window.URL.createObjectURL(blob);
          link.download = 'feature_statistics.zip';
          link.click();
        }, 

        error: (error) => {
          console.error('Error downloading feature statistics:', error);
        }
      });
  }


  configByGroupPlot(labels: Array<string>, datasets: Array<any>): void {
    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--text-color');
    const textColorSecondary = documentStyle.getPropertyValue('--text-color-secondary');
    const surfaceBorder = documentStyle.getPropertyValue('--surface-border');

    this.byGroupPlotData = {
      labels: labels,
      datasets: datasets
    }

    this.byGroupPlotOptions = {
      // indexAxis: 'y',
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

  configTokenCountPlot(labels: Array<string>, data: Array<number>) {
    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--text-color');

    this.tokenCountPlotData = {
      labels: labels,
      datasets: [{
        data: data
      }]
    }

    this.tokenCountPlotOptions = {
      cutout: '60%',
      plugins: {
          legend: {
              labels: {
                  color: textColor
              }
          }
      }
    };
  }


  makePlot(): void {
    this.featureService.selectedFeatures$
      .subscribe((features) => {
        this.selectedFeatures = features;
        this.selectedNonAuxiliaryFeatures = features.filter((feature) => !feature.is_auxiliary)
      });

    this.featureService.getStatisticsByLabel().subscribe({
      next: (raw) => {
        const df: Array<any> = parse(raw, { delimiter: "\t", header: true }).data.slice(0, -1)
        const tokenCountPlotData: { labels: string[], data: number[] } = {
          labels: [],
          data: []
        }; 
        let datasetsByGroup: Array<any> = [];

        df.forEach((obj) => {
          // Get data for token count:
          tokenCountPlotData.labels.push(obj['label'])
          tokenCountPlotData.data.push(obj['total_token_count'])

          // Get data for feature statistics:
          let currentFeatureData: Array<number> = [];

          this.selectedNonAuxiliaryFeatures.forEach((feature) => {
            currentFeatureData.push(obj[feature.annotation_method])
          })

          datasetsByGroup.push({
              label: obj["label"],
              data: currentFeatureData
          })
        })

        this.configTokenCountPlot(tokenCountPlotData.labels, tokenCountPlotData.data);
        this.configByGroupPlot(this.selectedNonAuxiliaryFeatures.map(feature => feature.name), datasetsByGroup)
      }
    })
  }

  ngOnInit() {
    this.makePlot();    
  }  
}
