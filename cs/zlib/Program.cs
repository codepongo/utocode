using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System.IO.Compression;
using ComponentAce.Compression.Libs.zlib;

namespace unzipecgfile
{
    class Program
    {




        static void Main(string[] args)
        {
            Action inflation = () =>
             {
                 string hizlib = "hi,zlib!";

                 FileStream zip = new FileStream(args[0], System.IO.FileMode.Create);
                 ZOutputStream o = new ZOutputStream(zip, zlibConst.Z_DEFAULT_COMPRESSION);
                 Stream s = new MemoryStream(System.Text.Encoding.UTF8.GetBytes(hizlib));
                 try
                 {
                     Action<Stream, Stream> copyStream = (Stream input, Stream output) =>
                     {
                         byte[] buffer = new byte[4096];
                         int len;
                         while ((len = input.Read(buffer, 0, 4096)) > 0)
                         {
                             output.Write(buffer, 0, len);
                         }
                         output.Flush();
                     };
                     copyStream(s, o);
                 }
                 finally
                 {
                     o.Close();
                     zip.Close();
                     s.Close();
                 }


             };
            inflation();

            Action deflation = () =>
            {
                FileStream zip = new System.IO.FileStream(args[0], System.IO.FileMode.Open);
                FileStream txt = new System.IO.FileStream(args[1], System.IO.FileMode.Create);
                ZInputStream unzip = new ZInputStream(zip);
                try
                {
                    Action<ZInputStream, Stream> copyStream = (ZInputStream input, Stream output) =>
                    {
                        byte[] buffer = new byte[4096];
                        int len;
                        while ((len = input.read(buffer, 0, 4096)) > 0)
                        {
                            output.Write(buffer, 0, len);
                        }
                        output.Flush();
                    };
                    copyStream(unzip, txt);
                }
                finally
                {
                    unzip.Close();
                    txt.Close();
                    zip.Close();
                }
            };
            deflation();

        }
    }
}
