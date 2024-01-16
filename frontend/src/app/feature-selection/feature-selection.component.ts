import { Component, EventEmitter, OnInit, Output, SimpleChange, SimpleChanges } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { FeatureService } from './feature.service';
import { IFeature } from './feature';

@Component({
  selector: 'app-feature-selection',
  templateUrl: './feature-selection.component.html',
  styleUrls: ['./feature-selection.component.css']
})
export class FeatureSelectionComponent implements OnInit {
  @Output() featureSelectionEvent: EventEmitter<boolean> = new EventEmitter()

  toggleButtonChecked: boolean = true;
  selectedFeatures: Array<IFeature> = [];
  allFeatures: Array<IFeature> = [];
  selectedDimensions: Array<string> = [];
  allDimensions: Array<string> = [];
  errorMsg: any;

  constructor(private featureService: FeatureService) {

  }

  onToggleSelectAll(): void {
    if(this.toggleButtonChecked === false) {
      this.featureService.getAllFeatures()
        .subscribe({
          next: (data) => {
            this.selectedFeatures = data;
            this.selectedDimensions = [...new Set(data.map((item) => item.dimension))];
            this.featureService.setSelectedFeatures(this.selectedFeatures);
            this.updateFeatureSelectionStatus();
          }
        })
    } else {
      this.selectedFeatures = [];
      this.selectedDimensions = [];
      this.featureService.setSelectedFeatures(this.selectedFeatures);
      this.updateFeatureSelectionStatus();
    }
  }

  changeToggleButtonStatus(): void {
    this.selectedFeatures.length === 0 ? this.toggleButtonChecked  = true : this.toggleButtonChecked = false;
  }

  onSelectFeature(event: any): void {
    const dimensionsOfSelectedFeatures = [...new Set(event.checked.map((item: { dimension: string; }) => item.dimension))];
    let allDimensionsSelected: Array<string> = [];
    
    if (dimensionsOfSelectedFeatures.length > 0) {
      dimensionsOfSelectedFeatures.forEach((dimension) => {
        const allFeaturesInDimension = this.allFeatures.filter((feature) => feature.dimension === dimension);
        const selectedFeaturesOfDimension = this.selectedFeatures.filter((feature) => feature.dimension === dimension);

        if (selectedFeaturesOfDimension.length === allFeaturesInDimension.length) {
          if (!allDimensionsSelected.includes(dimension as string)) {
            allDimensionsSelected.push(dimension as string);
          }
        } else {
          allDimensionsSelected.filter((item) => item !== dimension);
        }
      })
    } else {
      allDimensionsSelected = [];
    }

    this.changeToggleButtonStatus();
    this.selectedDimensions = allDimensionsSelected;
    this.featureService.setSelectedFeatures(this.selectedFeatures);
    this.updateFeatureSelectionStatus();
  }

  onSelectDimension(dimension: string): void {
    const dimensionIndex = this.selectedDimensions.indexOf(dimension);
  
    if (dimensionIndex !== -1) {
      const featuresOfDimension = this.allFeatures.filter((feature) => feature.dimension === dimension);
      this.selectedFeatures = [...this.selectedFeatures, ...featuresOfDimension];
      this.selectedDimensions.push(dimension);
    } else {
      this.selectedDimensions.splice(dimensionIndex, 1);
      this.selectedFeatures = this.selectedFeatures.filter((feature) => feature.dimension !== dimension);
    }
  
    this.changeToggleButtonStatus();
    this.featureService.setSelectedFeatures(this.selectedFeatures);
    this.updateFeatureSelectionStatus();
  }

  updateFeatureSelectionStatus(): void {
    this.selectedFeatures.length === 0 
      ? this.featureSelectionEvent.emit(false)
      : this.featureSelectionEvent.emit(true);
  }

  ngOnInit() {
    this.featureService.getAllFeatures().subscribe({
      next: data => {
        this.allFeatures = data;
        this.allDimensions = [...new Set(data.map((item) => item.dimension))]
      }
    })

    this.featureService.setSelectedFeatures(this.selectedFeatures);
  }
}
