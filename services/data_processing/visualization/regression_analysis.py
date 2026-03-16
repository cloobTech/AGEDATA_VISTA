import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


def linear_regression_plot(X_test, y_test, y_pred, feature_names=None) -> dict:
    """Generate professional linear regression visualizations"""
    num_features = X_test.shape[1]
    
    if feature_names is None:
        feature_names = [f"Feature {i+1}" for i in range(num_features)]

    # Convert to DataFrame for easier px usage
    df = pd.DataFrame(X_test, columns=feature_names)
    df['Actual'] = y_test
    df['Predicted'] = y_pred
    
    # Calculate performance metrics
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    metrics_text = f"<br><sup>MSE: {mse:.3f} | MAE: {mae:.3f} | R²: {r2:.3f}</sup>"
    
    plots = {}

    if num_features == 1:
        feature = feature_names[0]
        
        # Create main plot
        fig = go.Figure()
        
        # Actual values
        fig.add_trace(go.Scatter(
            x=df[feature],
            y=df['Actual'],
            mode='markers',
            name='Actual Values',
            marker=dict(
                color='#1f77b4',
                size=8,
                opacity=0.7,
                line=dict(width=1, color='DarkSlateGrey')
            ),
            hovertemplate=f"{feature}: %{{x:.3f}}<br>Actual: %{{y:.3f}}<extra></extra>"
        ))
        
        # Predicted line
        sorted_df = df.sort_values(by=feature)
        fig.add_trace(go.Scatter(
            x=sorted_df[feature],
            y=sorted_df['Predicted'],
            mode='lines',
            name='Regression Line',
            line=dict(color='red', width=3),
            hovertemplate=f"{feature}: %{{x:.3f}}<br>Predicted: %{{y:.3f}}<extra></extra>"
        ))
        
        # Perfect prediction line
        min_val = min(df[feature].min(), df['Actual'].min())
        max_val = max(df[feature].max(), df['Actual'].max())
        fig.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode='lines',
            name='Perfect Fit',
            line=dict(color='green', dash='dash', width=2),
            hovertemplate="Perfect Prediction Line<extra></extra>"
        ))
        
        fig.update_layout(
            title=dict(
                text=f"Linear Regression Fit{metrics_text}",
                x=0.05,
                xanchor='left',
                font=dict(size=20, color='#2a3f5f')
            ),
            xaxis_title=feature,
            yaxis_title="Target Value",
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#E5ECF6',
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='#2a3f5f'
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#E5ECF6',
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='#2a3f5f'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            width=800,
            height=600,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(255, 255, 255, 0.9)'
            ),
            hovermode='closest'
        )
        
        plots["linear_reg_plot"] = fig.to_json()
        
        # Residual plot
        residuals = y_test - y_pred
        fig_res = go.Figure()
        
        fig_res.add_trace(go.Scatter(
            x=df[feature],
            y=residuals,
            mode='markers',
            name='Residuals',
            marker=dict(
                color='#ff7f0e',
                size=8,
                opacity=0.7,
                line=dict(width=1, color='DarkSlateGrey')
            ),
            hovertemplate=f"{feature}: %{{x:.3f}}<br>Residual: %{{y:.3f}}<extra></extra>"
        ))
        
        # Zero reference line
        fig_res.add_hline(
            y=0, 
            line_dash="dash", 
            line_width=2, 
            line_color='#2a3f5f',
            annotation_text="Zero Residual", 
            annotation_position="top right"
        )
        
        # Add confidence bands (2 standard deviations)
        residual_std = np.std(residuals)
        if np.isfinite(residual_std) and residual_std > 0:
            fig_res.add_hrect(
                y0=-2*residual_std,
                y1=2*residual_std,
                fillcolor="rgba(0, 0, 0, 0.1)",
                line_width=0,
                annotation_text="±2σ",
                annotation_position="bottom right"
            )
        
        fig_res.update_layout(
            title=dict(
                text=f"Residual Analysis - {feature}",
                x=0.05,
                xanchor='left',
                font=dict(size=18, color='#2a3f5f')
            ),
            xaxis_title=feature,
            yaxis_title="Residuals",
            plot_bgcolor='white',
            paper_bgcolor='white',
            width=800,
            height=500,
            showlegend=False,
            hovermode='closest'
        )
        
        plots["residual_plot"] = fig_res.to_json()
        
    else:
        # For multiple features, create individual plots
        for feature in feature_names:
            fig = go.Figure()
            
            # Actual values
            fig.add_trace(go.Scatter(
                x=df[feature],
                y=df['Actual'],
                mode='markers',
                name='Actual Values',
                marker=dict(
                    color='#1f77b4',
                    size=8,
                    opacity=0.7,
                    line=dict(width=1, color='DarkSlateGrey')
                ),
                hovertemplate=f"{feature}: %{{x:.3f}}<br>Actual: %{{y:.3f}}<extra></extra>"
            ))
            
            # Predicted values (sorted for line)
            sorted_df = df.sort_values(by=feature)
            fig.add_trace(go.Scatter(
                x=sorted_df[feature],
                y=sorted_df['Predicted'],
                mode='lines',
                name='Regression Fit',
                line=dict(color='red', width=3),
                hovertemplate=f"{feature}: %{{x:.3f}}<br>Predicted: %{{y:.3f}}<extra></extra>"
            ))
            
            fig.update_layout(
                title=dict(
                    text=f"Linear Regression - {feature}{metrics_text}",
                    x=0.05,
                    xanchor='left',
                    font=dict(size=18, color='#2a3f5f')
                ),
                xaxis_title=feature,
                yaxis_title="Target Value",
                plot_bgcolor='white',
                paper_bgcolor='white',
                width=700,
                height=500,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                ),
                hovermode='closest'
            )
            
            plots[f"linear_reg_{feature}"] = fig.to_json()

    return plots


def decision_tree_plot(X_test, y_test, y_pred, feature_names=None) -> dict:
    """Generate professional decision tree visualizations"""
    plots = {}

    if feature_names is None:
        feature_names = [f"Feature {i+1}" for i in range(X_test.shape[1])]

    # Calculate performance metrics
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    metrics_text = f"<br><sup>MSE: {mse:.3f} | MAE: {mae:.3f} | R²: {r2:.3f}</sup>"
    
    # Actual vs Predicted scatter plot
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=y_test,
        y=y_pred,
        mode='markers',
        name='Predictions',
        marker=dict(
            color='#1f77b4',
            size=8,
            opacity=0.7,
            line=dict(width=1, color='DarkSlateGrey')
        ),
        hovertemplate="Actual: %{x:.3f}<br>Predicted: %{y:.3f}<extra></extra>"
    ))
    
    # Perfect prediction line
    min_val = min(y_test.min(), y_pred.min())
    max_val = max(y_test.max(), y_pred.max())
    fig.add_trace(go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode='lines',
        name='Perfect Prediction',
        line=dict(color='red', dash='dash', width=2.5),
        hovertemplate="Perfect Prediction Line<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(
            text=f"Decision Tree Performance{metrics_text}",
            x=0.05,
            xanchor='left',
            font=dict(size=20, color='#2a3f5f')
        ),
        xaxis_title="Actual Values",
        yaxis_title="Predicted Values",
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='#2a3f5f'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='#2a3f5f'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=700,
        height=600,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        hovermode='closest'
    )
    
    plots["actual_vs_predicted"] = fig.to_json()
    
    # Residual plot
    residuals = y_test - y_pred
    fig_res = go.Figure()
    
    fig_res.add_trace(go.Scatter(
        x=y_pred,
        y=residuals,
        mode='markers',
        name='Residuals',
        marker=dict(
            color='#ff7f0e',
            size=8,
            opacity=0.7,
            line=dict(width=1, color='DarkSlateGrey')
        ),
        hovertemplate="Predicted: %{x:.3f}<br>Residual: %{y:.3f}<extra></extra>"
    ))
    
    # Zero reference line
    fig_res.add_hline(
        y=0, 
        line_dash="dash", 
        line_width=2, 
        line_color='#2a3f5f',
        annotation_text="Zero Residual", 
        annotation_position="top right"
    )
    
    # Add confidence bands (2 standard deviations)
    residual_std = np.std(residuals)
    if np.isfinite(residual_std) and residual_std > 0:
        fig_res.add_hrect(
            y0=-2*residual_std,
            y1=2*residual_std,
            fillcolor="rgba(0, 0, 0, 0.1)",
            line_width=0,
            annotation_text="±2σ",
            annotation_position="bottom right"
        )
    
    fig_res.update_layout(
        title=dict(
            text="Decision Tree Residual Analysis",
            x=0.05,
            xanchor='left',
            font=dict(size=18, color='#2a3f5f')
        ),
        xaxis_title="Predicted Values",
        yaxis_title="Residuals",
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=700,
        height=500,
        showlegend=False,
        hovermode='closest'
    )
    
    plots["residual_plot"] = fig_res.to_json()
    
    # Feature-specific plots (for important features)
    for idx, feature in enumerate(feature_names[:3]):  # Limit to top 3 features
        df = pd.DataFrame({
            feature: X_test[:, idx],
            "Actual": y_test,
            "Predicted": y_pred
        })

        fig = go.Figure()
        
        # Actual values
        fig.add_trace(go.Scatter(
            x=df[feature],
            y=df['Actual'],
            mode='markers',
            name='Actual',
            marker=dict(
                color='#1f77b4',
                size=8,
                opacity=0.7,
                line=dict(width=1, color='DarkSlateGrey')
            ),
            hovertemplate=f"{feature}: %{{x:.3f}}<br>Actual: %{{y:.3f}}<extra></extra>"
        ))
        
        # Predicted values
        fig.add_trace(go.Scatter(
            x=df[feature],
            y=df['Predicted'],
            mode='markers',
            name='Predicted',
            marker=dict(
                color='#ff7f0e',
                size=8,
                opacity=0.7,
                line=dict(width=1, color='DarkSlateGrey')
            ),
            hovertemplate=f"{feature}: %{{x:.3f}}<br>Predicted: %{{y:.3f}}<extra></extra>"
        ))
        
        fig.update_layout(
            title=dict(
                text=f"Decision Tree - {feature}",
                x=0.05,
                xanchor='left',
                font=dict(size=16, color='#2a3f5f')
            ),
            xaxis_title=feature,
            yaxis_title="Target Value",
            plot_bgcolor='white',
            paper_bgcolor='white',
            width=600,
            height=500,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            hovermode='closest'
        )
        
        plots[f"feature_{feature}"] = fig.to_json()

    return plots


# Additional: Partial Dependence Plot for linear regression
def generate_partial_dependence_plot(model, X_test, feature_names, feature_index):
    """Generate partial dependence plot for linear regression"""
    # Create grid of values for the feature
    feature_values = np.linspace(X_test[:, feature_index].min(), 
                               X_test[:, feature_index].max(), 
                               100)
    
    # Create data for partial dependence
    X_temp = X_test.copy()
    predictions = []
    
    for value in feature_values:
        X_temp[:, feature_index] = value
        preds = model.predict(X_temp)
        predictions.append(np.mean(preds))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=feature_values,
        y=predictions,
        mode='lines',
        name='Partial Dependence',
        line=dict(color='#1f77b4', width=3),
        hovertemplate=f"{feature_names[feature_index]}: %{{x:.3f}}<br>Prediction: %{{y:.3f}}<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(
            text=f"Partial Dependence - {feature_names[feature_index]}",
            x=0.05,
            xanchor='left',
            font=dict(size=18, color='#2a3f5f')
        ),
        xaxis_title=feature_names[feature_index],
        yaxis_title="Partial Dependence",
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=700,
        height=500
    )
    
    return fig.to_json()