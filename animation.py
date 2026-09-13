from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image
import os


def style_animation(ax):
    ax.set_title('Top 10 Countries by Population Over Time')
    ax.set_xlabel('Population')
    ax.set_ylabel('Country')


def load_flag_images(df, flag_folder):
    """Load and resize all flag images once at startup"""

    flag_images = {}

    for iso_code in df['ISO3_code'].dropna().unique():

        flag_path = os.path.join(
            flag_folder,
            f"{iso_code}.png"
        )

        try:
            img = Image.open(flag_path).convert("RGBA")
            img.thumbnail((50, 30), Image.Resampling.LANCZOS)

            flag_images[iso_code] = img

            print(f"Loaded: {iso_code}")

        except Exception as e:
            print(f"Could not load {iso_code}: {e}")

    return flag_images


def write_year(ax, year):
    ax.text(
        0.95,
        0.05,
        str(year),
        transform=ax.transAxes,
        fontsize=12,
        color='gray',
        ha='right',
        va='bottom'
    )


def create_animation(df, flag_folder):

    fig, ax = plt.subplots(figsize=(10, 5))

    frames = sorted(df['Time'].unique())

    # Load flags once
    flag_images = load_flag_images(df, flag_folder)

    def animate(frame):

        ax.clear()

        # Get data for current year
        pop_data_frame = df[df['Time'] == frame]

        # Get top 10 countries
        top_countries = (
            pop_data_frame
            .nlargest(10, 'TPopulation1Jan')
            .sort_values('TPopulation1Jan', ascending=True)
            .reset_index(drop=True)
        )

        # Draw bars
        ax.barh(
            top_countries['Location'],
            top_countries['TPopulation1Jan']
        )

        # Add population numbers
        for i in range(len(top_countries)):

            population = top_countries['TPopulation1Jan'].iloc[i]

            ax.text(
                population,
                i,
                f"{population:,.0f}",
                va='center',
                ha='left'
            )

        # Leave some space on the left for flags
        max_population = top_countries['TPopulation1Jan'].max()

        ax.set_xlim(
            left=-max_population * 0.12,
            right=max_population * 1.15
        )

        # Title and year
        style_animation(ax)
        write_year(ax, frame)

        # Add flags
        for i, row in top_countries.iterrows():

            iso_code = row['ISO3_code']

            if iso_code in flag_images:

                img_box = OffsetImage(
                    flag_images[iso_code],
                    zoom=0.7
                )

                ab = AnnotationBbox(
                    img_box,
                    (0, i),
                    xybox=(-35, 0),
                    xycoords='data',
                    boxcoords='offset points',
                    frameon=False,
                    box_alignment=(1, 0.5)
                )

                ax.add_artist(ab)

        plt.tight_layout()


    anim = animation.FuncAnimation(
        fig,
        animate,
        frames=frames,
        interval=200
    )

    return anim


if __name__ == "__main__":

    df = pd.read_csv(
        'C:/Users/user/Documents/Time_series_in python/data/cleaned_country_data.csv'
    )

    flag_folder = (
        'C:/Users/user/Documents/Time_series_in python/flags'
    )

    anim = create_animation(df, flag_folder)

    # Save as MP4
    anim.save('video.mp4', writer='ffmpeg', fps=30)

    plt.show()