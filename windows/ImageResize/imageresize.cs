using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Drawing.Drawing2D;

namespace Tutorial
{
	class ImageResize
	{
		enum Dimensions 
		{
			Width,
			Height
		}
		enum AnchorPosition
		{
			Top,
			Center,
			Bottom,
			Left,
			Right
		}
		[STAThread]
		static void Main(string[] args)
		{
            if (args.Length < 4)
            {
                Help();
                return;
            }
            string input = "";
            string output = "";
            int percent = 0;
            int i = 0;
            while( i < args.Length)
            {
                if (args[i] == "-i")
                {
                    i++;
                    if (i < args.Length)
                    {
                        input = args[i];
                    }
                    else
                    {
                        Help();
                        return;
                    }
                }
                else if (args[i] == "-s")
                {
                    i++;
                    if (i < args.Length)
                    {
                        percent = int.Parse(args[i]); 
                        
                    }
                    else
                    {
                        Help();
                        return;
                    }
                }
                else
                {
                    output = args[i];
                }
                i++;

            }
            if (input == "" || output == "" || percent == 0)
            {
                Help();
                return;
            }


			//create a image object containing a verticel photograph
			Image from = Image.FromFile(input);

            Image to = ScaleByPercent(from, percent);
            to.Save(output, ImageFormat.Jpeg);
			to.Dispose();

		}
        static void Help()
        {
            Console.Write(System.IO.Path.GetFileName(System.Reflection.Assembly.GetExecutingAssembly().CodeBase) +
@" <output> <-i input> <-s percent> [-help]
output - output image file name
-i input - input image file name
-s percent  - scale percent such as -s 70 means sclae 70%
-h - print help information");
        }
		static Image ScaleByPercent(Image imgPhoto, int Percent)
		{
			float nPercent = ((float)Percent/100);

			int sourceWidth = imgPhoto.Width;
			int sourceHeight = imgPhoto.Height;
			int sourceX = 0;
			int sourceY = 0;

			int destX = 0;
			int destY = 0; 
			int destWidth  = (int)(sourceWidth * nPercent);
			int destHeight = (int)(sourceHeight * nPercent);

			Bitmap bmPhoto = new Bitmap(destWidth, destHeight, PixelFormat.Format24bppRgb);
			bmPhoto.SetResolution(imgPhoto.HorizontalResolution, imgPhoto.VerticalResolution);

			Graphics grPhoto = Graphics.FromImage(bmPhoto);
			grPhoto.InterpolationMode = InterpolationMode.HighQualityBicubic;

			grPhoto.DrawImage(imgPhoto, 
				new Rectangle(destX,destY,destWidth,destHeight),
				new Rectangle(sourceX,sourceY,sourceWidth,sourceHeight),
				GraphicsUnit.Pixel);

			grPhoto.Dispose();
			return bmPhoto;
		}
        //static Image ConstrainProportions(Image imgPhoto, int Size, Dimensions Dimension)
        //{
        //    int sourceWidth = imgPhoto.Width;
        //    int sourceHeight = imgPhoto.Height;
        //    int sourceX = 0;
        //    int sourceY = 0;
        //    int destX = 0;
        //    int destY = 0; 
        //    float nPercent = 0;

        //    switch(Dimension)
        //    {
        //        case Dimensions.Width:
        //            nPercent = ((float)Size/(float)sourceWidth);
        //            break;
        //        default:
        //            nPercent = ((float)Size/(float)sourceHeight);
        //            break;
        //    }
				
        //    int destWidth  = (int)(sourceWidth * nPercent);
        //    int destHeight = (int)(sourceHeight * nPercent);

        //    Bitmap bmPhoto = new Bitmap(destWidth, destHeight, PixelFormat.Format24bppRgb);
        //    bmPhoto.SetResolution(imgPhoto.HorizontalResolution, imgPhoto.VerticalResolution);

        //    Graphics grPhoto = Graphics.FromImage(bmPhoto);
        //    grPhoto.InterpolationMode = InterpolationMode.HighQualityBicubic;

        //    grPhoto.DrawImage(imgPhoto, 
        //    new Rectangle(destX,destY,destWidth,destHeight),
        //    new Rectangle(sourceX,sourceY,sourceWidth,sourceHeight),
        //    GraphicsUnit.Pixel);

        //    grPhoto.Dispose();
        //    return bmPhoto;
        //}

        //static Image FixedSize(Image imgPhoto, int Width, int Height)
        //{
        //    int sourceWidth = imgPhoto.Width;
        //    int sourceHeight = imgPhoto.Height;
        //    int sourceX = 0;
        //    int sourceY = 0;
        //    int destX = 0;
        //    int destY = 0; 

        //    float nPercent = 0;
        //    float nPercentW = 0;
        //    float nPercentH = 0;

        //    nPercentW = ((float)Width/(float)sourceWidth);
        //    nPercentH = ((float)Height/(float)sourceHeight);

        //    //if we have to pad the height pad both the top and the bottom
        //    //with the difference between the scaled height and the desired height
        //    if(nPercentH < nPercentW)
        //    {
        //        nPercent = nPercentH;
        //        destX = (int)((Width - (sourceWidth * nPercent))/2);
        //    }
        //    else
        //    {
        //        nPercent = nPercentW;
        //        destY = (int)((Height - (sourceHeight * nPercent))/2);
        //    }
		
        //    int destWidth  = (int)(sourceWidth * nPercent);
        //    int destHeight = (int)(sourceHeight * nPercent);

        //    Bitmap bmPhoto = new Bitmap(Width, Height, PixelFormat.Format24bppRgb);
        //    bmPhoto.SetResolution(imgPhoto.HorizontalResolution, imgPhoto.VerticalResolution);

        //    Graphics grPhoto = Graphics.FromImage(bmPhoto);
        //    grPhoto.Clear(Color.Red);
        //    grPhoto.InterpolationMode = InterpolationMode.HighQualityBicubic;

        //    grPhoto.DrawImage(imgPhoto, 
        //        new Rectangle(destX,destY,destWidth,destHeight),
        //        new Rectangle(sourceX,sourceY,sourceWidth,sourceHeight),
        //        GraphicsUnit.Pixel);

        //    grPhoto.Dispose();
        //    return bmPhoto;
        //}
        //static Image Crop(Image imgPhoto, int Width, int Height, AnchorPosition Anchor)
        //{
        //    int sourceWidth = imgPhoto.Width;
        //    int sourceHeight = imgPhoto.Height;
        //    int sourceX = 0;
        //    int sourceY = 0;
        //    int destX = 0;
        //    int destY = 0;

        //    float nPercent = 0;
        //    float nPercentW = 0;
        //    float nPercentH = 0;

        //    nPercentW = ((float)Width/(float)sourceWidth);
        //    nPercentH = ((float)Height/(float)sourceHeight);

        //    if(nPercentH < nPercentW)
        //    {
        //        nPercent = nPercentW;
        //        switch(Anchor)
        //        {
        //            case AnchorPosition.Top:
        //                destY = 0;
        //                break;
        //            case AnchorPosition.Bottom:
        //                destY = (int)(Height - (sourceHeight * nPercent));
        //                break;
        //            default:
        //                destY = (int)((Height - (sourceHeight * nPercent))/2);
        //                break;
        //        }				
        //    }
        //    else
        //    {
        //        nPercent = nPercentH;
        //        switch(Anchor)
        //        {
        //            case AnchorPosition.Left:
        //                destX = 0;
        //                break;
        //            case AnchorPosition.Right:
        //                destX = (int)(Width - (sourceWidth * nPercent));
        //                break;
        //            default:
        //                destX = (int)((Width - (sourceWidth * nPercent))/2);
        //                break;
        //        }			
        //    }

        //    int destWidth  = (int)(sourceWidth * nPercent);
        //    int destHeight = (int)(sourceHeight * nPercent);

        //    Bitmap bmPhoto = new Bitmap(Width, Height, PixelFormat.Format24bppRgb);
        //    bmPhoto.SetResolution(imgPhoto.HorizontalResolution, imgPhoto.VerticalResolution);

        //    Graphics grPhoto = Graphics.FromImage(bmPhoto);
        //    grPhoto.InterpolationMode = InterpolationMode.HighQualityBicubic;

        //    grPhoto.DrawImage(imgPhoto, 
        //        new Rectangle(destX,destY,destWidth,destHeight),
        //        new Rectangle(sourceX,sourceY,sourceWidth,sourceHeight),
        //        GraphicsUnit.Pixel);

        //    grPhoto.Dispose();
        //    return bmPhoto;
        //}
	}
}
